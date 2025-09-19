#!/bin/sh
#set -x
mkdir audio > /dev/null 2>&1
scrdir=`dirname "$0"`
if test -f models/silero_vad.jit; then
    :
else
    cd models
    wget https://github.com/snakers4/silero-vad/raw/master/src/silero_vad/data/silero_vad.jit
    # Download models for speaker identification
    wget https://cloud.dfki.de/owncloud/index.php/s/rjbyoJ5XnaxpNpm/download/spkident_model.tar.gz
    tar xf spkident_model.tar.gz && rm spkident_model.tar.gz
    cd ..
fi

if test "$1" = "-l"; then
    exit 0
fi

download_models() { uv run download_models.py "$1"; }

if test -z "$1"; then
    download_models large-v3-turbo
else
    download_models "$@"
fi
