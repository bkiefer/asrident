#!/usr/bin/env python3

import os
from pathlib import Path
import numpy as np
from sklearn.preprocessing import normalize
from scipy.spatial.distance import cosine
from speechbrain.inference import EncoderClassifier, LocalStrategy
os.environ["KERAS_BACKEND"] = "torch"
from keras import models
import torchaudio


class SpeakerIdent:

    def __init__(self, model_root: Path):
        self.ecapa_tdnn = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir=model_root / 'spkrec-ecapa-voxceleb',
            local_strategy=LocalStrategy.NO_LINK,
            huggingface_cache_dir=model_root / 'spkrec-ecapa-voxceleb'
        )

        # Load pretrained autoencoder
        self.encoder = models.load_model('models/autoencoder.keras')

        self.max_speaker_embeddings = 10

        self.speaker_database = {}

        self.RELATIVE_THRESHOLD = 0.1
        self.ABSOLUTE_THRESHOLD = 0.5

        self.calls = 0
        self.mean_best = 0
        self.mean_best_diff = 0

    def generate_embedding(self, signal):
        embedding = self.ecapa_tdnn.encode_batch(signal).squeeze().detach().cpu().numpy()
        return embedding


    def load_audio(self, path, num_frames=-1):
        signal, sr = torchaudio.load(path, channels_first=False,
                                     num_frames=num_frames)
        return self.ecapa_tdnn.audio_normalizer(signal, sr)


    def add_speaker(self, embedding, speaker_id):
        """
        Add a speaker embedding to the database to build it up incrementally.
        Currently an incremental mean is computed for each speaker, up to
        max_speaker_embeddings.

        :param embedding: a normalized embedding computed by ecapa_tdnn
        :param speaker_id: a speaker id
        :return: void
        """
        if speaker_id not in self.speaker_database:
            self.speaker_database[speaker_id] = [embedding, 1]
        else:
            if self.speaker_database[speaker_id][1] < self.max_speaker_embeddings:
                # compute incremental average
                factor = self.speaker_database[speaker_id][1]
                self.speaker_database[speaker_id][1] = factor + 1  # n
                factor = factor / (factor + 1)  # n - 1 / n
                self.speaker_database[speaker_id][0] = \
                        (self.speaker_database[speaker_id][0] * factor # sum(1_n-1)
                         + embedding) / self.speaker_database[1]


    # function for spk identification
    # first create embeddings
    # pass it through autoencoder and get only encoder output
    # normalise the embeddings
    # compute cosine distance between each of 5 speakers from database with new
    # embedding, then the best similarity value is picked and assigned that speaker
    def identify_speaker(self, audio_chunk):
        """
        function for speaker identification
        first create embeddings
        pass it through autoencoder and get only encoder output
        normalise the embeddings
        compute cosine distance between each of 5 speakers from database with new
        embedding, then the best similarity value is picked and assigned that speaker

        :param audio_chunk: a tensor containing a mono audio sample in 16kHz
               sample rate, 32 bit floating point
        :return: the most similar speaker, or 'Unknown' if no speaker is similar
                 enough
        """
        embedding = self.generate_embedding(audio_chunk)
        embedding = np.expand_dims(embedding, axis=0)  # add batch dimension
        # Encode with autoencoder, reduce dimensionality
        embedding = self.encoder.predict(embedding)
        # Normalize
        embedding = normalize(embedding, axis=1)[0]

        best_match = None
        best_similarity = -1.0
        second_best_sim = -1.0
        for speaker, spkembedding in self.speaker_database.items():
            similarity = 1 - cosine(embedding, spkembedding[0])
            if similarity > best_similarity:
                second_best_sim = best_similarity
                best_similarity = similarity
                best_match = speaker
        factor = self.calls
        self.calls += 1
        self.mean_best = ((self.mean_best * factor) + best_similarity) / self.calls
        if second_best_sim > 0 :
            self.mean_best_diff = ((self.mean_best_diff * factor)
                                   + best_similarity - second_best_sim) / self.calls
            if best_similarity - second_best_sim < self.RELATIVE_THRESHOLD:
                best_match = "Unknown"
        elif best_similarity < self.ABSOLUTE_THRESHOLD:
            best_match = "Unknown"
        return best_match, float(best_similarity), embedding
