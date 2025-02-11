#!/usr/bin/env python3
from speechbrain.inference import EncoderClassifier
EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb",
                               savedir='pretrained_models/spkrec-ecapa-voxceleb")
