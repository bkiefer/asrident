#!/bin/sh
#set -x
mkdir audio > /dev/null 2>&1
here=`pwd`
scrdir=`dirname "$0"`
cd $scrdir
# Not using $scrdir since we assume the cd there!!

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

download_models() {
    version=`grep version "pyproject.toml" | sed 's/version *= *"\([^"]*\)".*/\1/'`
    # uv can not be used since it is owned by root!
    docker run --rm --user "$(id -u):$(id -g)" \
           -v "./download_models.py:/app/download_models.py" \
           -v "./models":/app/models \
           -e HF_HOME=/app/models \
           asrident:$version \
           /bin/bash -c ". .venv/bin/activate ; python download_models.py $@"
    test -d models/whisper
}

if test -z "$1"; then
    download_models large-v3-turbo
else
    download_models "$@"
fi
