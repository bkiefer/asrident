#!/usr/bin/env python3

from pathlib import Path
import torch
import logging
import json

from transcriptor import WhisperMicroServer, main, logger
from spkident import SpeakerIdent


# configure logger
logger.setLevel(logging.INFO)

modroot = Path('.') / 'models'


class WhisperAsrIdentServer(WhisperMicroServer):
    """
    Like WhisperMicroServer, but also doing speaker identification.

    Speaker indentification based on audio and (if available) external hints.
    """

    def __init__(self, config, transcription_file=None):
        """Initialize speaker identification and transcription."""
        super().__init__(config, transcription_file)
        self.__init_speaker_identification()

    def __init_speaker_identification(self):
        self.spkident = SpeakerIdent(modroot)
        self.embeddings = []
        self.speaker_identification_topic = self.pid + '/speakeridentification'
        self.topics[self.speaker_identification_topic] = self._on_speakerid_msg

    def _on_speakerid_msg(self, client, userdata, message):
        """Process json message telling us this is Speaker B, not Speaker A.

        We can identify the embedding using the unique id that was there when
        the estimation was sent.

        { "id": "<uniq_id>", "speaker": "<mkm:Einsatzkraftd713e1f2_52>" }
        """
        try:
            speaker_ident = json.loads(message.payload)
        except:
            return
        id = speaker_ident["id"]  # id is unique, check if we have embedding
        embedding_info = next((e for e in self.embeddings if e[0] == id), ())
        if embedding_info:
            spk_from_spk = speaker_ident["speaker"]
            id, emb, label = embedding_info
            self.embeddings.remove(embedding_info)
            logger.info(
                f'Add embedding for speaker {spk_from_spk}, not {label}')
            self.spkident.add_speaker(emb, spk_from_spk)

    def __speaker_identification(self, audio_segment, unique_id):
        fl32arr = torch.tensor(audio_segment, dtype=torch.float32)
        fl32arr /= 32768
        speaker, conf, embedding = self.spkident.identify_speaker(fl32arr)
        self.embeddings.append((unique_id, embedding, speaker))
        while len(self.embeddings) > 3:
            id, emb, label = self.embeddings.pop(0)
            if label != 'Unknown':
                # this recognition was not questioned, support detected speaker
                logger.debug(f"Support speaker {label}")
                self.spkident.add_speaker(emb, label)
        logger.info(f"Speaker identification: {speaker} {conf:.3f}")
        return {"speaker": speaker, "confidence": conf}

    def transcribe_success(self, result, audio_segment):
        """Do speaker identification after successful transcription."""
        unique_id = f'{result["source"]}_{result["start"]:d}'
        result.update({'id': unique_id})
        result.update(self.__speaker_identification(audio_segment, unique_id))
        super().transcribe_success(result, audio_segment)


if __name__ == '__main__':
    main(WhisperAsrIdentServer)
