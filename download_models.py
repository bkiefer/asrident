#!/usr/bin/env -S uv run --no-sync
from huggingface_hub import snapshot_download
from faster_whisper import utils
import sys

for model in sys.argv[1:] if len(sys.argv) > 1 else ['large-v3-turbo']:
     utils.download_model(model, cache_dir='models/whisper/',
                          output_dir='models/whisper/' + model)

snapshot_download(repo_id='speechbrain/spkrec-ecapa-voxceleb',
                  repo_type='model', local_dir='models/spkrec-ecapa-voxceleb')
