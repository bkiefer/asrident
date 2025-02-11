#!/bin/bash
#set -xe
if test -z "$1"; then
    echo "Usage: $0 <config.yml>"
    exit 1
fi
config="$1"
shift
scrdir=`dirname "$0"`
docker run -it \
       -e PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \
       --add-host host.docker.internal:host-gateway \
       -v ${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native \
       -v $HOME/.config/pulse/cookie:/root/.config/pulse/cookie \
       -v "$scrdir/$config":/app/config.yml \
       -v "$scrdir/whisper-models":/app/whisper-models \
       -v "$scrdir/audio":/app/audio \
       -v "$scrdir/outputs":/app/outputs \
       -v "$scrdir/TEval2015_day2":/app/TEval2015_day2 \
       --gpus=all asrident /bin/bash

#-c "./run_whisper.sh -o outputs -c config.yml $@"
