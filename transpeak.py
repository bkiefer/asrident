#!/usr/bin/env python3

from pathlib import Path
import logging
import torch
import json

from transcriptor import WhisperMicroServer, main
from spkident import SpeakerIdent


# configure logger
logging.basicConfig(
    format="%(asctime)s: %(levelname)s: %(message)s",
    level=logging.INFO)
logger = logging.getLogger(__file__)
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
        self.embeddings = {}
        self.embedid = 0
        self.speaker_identification_topic = self.pid + '/speakeridentification'
        self.topics[self.speaker_identification_topic] = self._on_speakerid_msg

    def _on_speakerid_msg(self, client, userdata, message):
        speaker_ident = json.loads(message.payload)
        id = speaker_ident["id"]
        spk_from_id = speaker_ident["embedid"]
        embedding = self.embeddings.pop(spk_from_id, None)
        spk_from_spk = speaker_ident["speaker"]
        logger.info(f'External {spk_from_id}: {spk_from_spk} for {id}')
        if embedding is not None:
            logger.info(f'Add embedding for speaker {spk_from_spk}')
            self.spkident.add_speaker(embedding, spk_from_spk)

    def __speaker_identification(self, audio_segment):
        logger.info("Attempting speaker identification...")
        fl32arr = torch.tensor(audio_segment, dtype=torch.float32)
        fl32arr /= 32768
        (speaker, conf, embedding) = self.spkident.identify_speaker(fl32arr)
        self.embedid += 1
        self.embeddings[self.embedid] = embedding
        return {"embedid": self.embedid, "speaker": speaker,
                "confidence": conf,
                }

    def transcribe_success(self, result, audio_segment):
        """Do speaker identification after successful transcription."""
        result.update({'id': f'{result["source"]}_{result["start"]:d}'})
        result.update(self.__speaker_identification(audio_segment))
        super().transcribe_success(result, audio_segment)


if __name__ == '__main__':
    main(WhisperAsrIdentServer)
