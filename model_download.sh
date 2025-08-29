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

download_models() {
    docker run --rm --user "$(id -u):$(id -g)" \
           -v "$scrdir/download_models.py:/app/download_models.py" \
           -v "$scrdir/models":/app/models \
           asrident:latest /app/download_models.py "$@"
}

if test -z "$1"; then
    download_models large-v2
else
    download_models "$@"
fi
