#!/usr/bin/env python3
from speechbrain.inference import EncoderClassifier, LocalStrategy
from faster_whisper import utils
import sys

for model in sys.argv[1:] if len(sys.argv) > 1 else ['large-v3-turbo']:
    utils.download_model(model, cache_dir='models/whisper/',
                         output_dir='models/whisper/' + model)

EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb",
                               savedir='models/spkrec-ecapa-voxceleb',
                               local_strategy=LocalStrategy.COPY_SKIP_CACHE,
                               huggingface_cache_dir="models/spkrec-ecapa-voxceleb")
