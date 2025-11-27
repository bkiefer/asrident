#!/bin/bash
#set -xe
if test -z "$1"; then
    echo "Usage: $0 <config.yml>"
    exit 1
fi
scrdir=`dirname "$0"`
config="$1"
shift
docker run -it \
       --device /dev/snd --group-add audio \
       -e PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \
       --add-host host.docker.internal:host-gateway \
       -v ${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulse/native \
       -v $HOME/.config/pulse/cookie:/root/.config/pulse/cookie \
       -v "$scrdir/${config}":/app/asrident/config.yml \
       -v "$scrdir/models":/app/asrident/models \
       -v "$scrdir/audio":/app/asrident/audio \
       -v "$scrdir/outputs":/app/asrident/outputs \
       --gpus=all \
       --entrypoint=/bin/bash \
       asrident -c "./run_whisper.sh -m -c config.yml"
