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
       --add-host host.docker.internal:host-gateway \
       --device /dev/snd --group-add audio \
       -v "$scrdir/${config}":/app/asrident/config.yml \
       -v "$scrdir/models":/app/asrident/models \
       -v "$scrdir/audio":/app/asrident/audio \
       -v "$scrdir/outputs":/app/asrident/outputs \
       --gpus=all \
       asrident /bin/bash -c "uv run ./run_whisper.sh -m -c config.yml"
