#!/usr/bin/env python3

from pathlib import Path
import torch
import logging
import json

from transcriptor import WhisperMicroServer, main, logger
from spkident import SpeakerIdent


# configure logger
logger.setLevel(logging.DEBUG)

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

        We can identify the embedding using the unique id that was there when the
        estimation was sent.

        { "id": "<uniq_id>", "speaker": "<mkm:Einsatzkraftd713e1f2_52>" }
        """
        try:
            speaker_ident = json.loads(message.payload)
        except:
            return
        id = speaker_ident["id"]  # id is unique
        embedding = next(e for e in self.embeddings if e[0] == id)
        spk_from_spk = speaker_ident["speaker"]
        logger.debug(f'External speaker info: {spk_from_spk} for {id}: {embedding}')
        if embedding is not None:
            embedding = embedding[1]
            logger.info(f'Add embedding for speaker {spk_from_spk}')
            self.spkident.add_speaker(embedding, spk_from_spk)

    def __speaker_identification(self, audio_segment, unique_id):
        logger.info("Attempting speaker identification...")
        fl32arr = torch.tensor(audio_segment, dtype=torch.float32)
        fl32arr /= 32768
        (speaker, conf, embedding) = self.spkident.identify_speaker(fl32arr)
        self.embeddings.append((unique_id, embedding))
        while len(self.embeddings) > 4:
            self.embeddings.pop(0)
        return {"speaker": speaker, "confidence": conf,}

    def transcribe_success(self, result, audio_segment):
        """Do speaker identification after successful transcription."""
        unique_id = f'{result["source"]}_{result["start"]:d}'
        result.update({'id': unique_id})
        result.update(self.__speaker_identification(audio_segment, unique_id))
        super().transcribe_success(result, audio_segment)


if __name__ == '__main__':
    main(WhisperAsrIdentServer)
