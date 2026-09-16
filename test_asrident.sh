#!/bin/sh
#set -x
MAX_TRIES=10
if test \! -d models/whisper/medium; then
    ./model_download.sh medium
fi

waitalive() {
    #echo "$@"
    try=1
    until eval $@; do
        echo -n $'\r'${try}
        sleep 3
        if test "$try" = "$MAX_TRIES"; then
            echo "Not starting after `expr 3 \* $try` seconds, failing"
            exit 1
        fi
        try=$(($try + 1))
    done
    echo
}

if docker images 2>&1 | grep -q asrident; then
    DOCKER_ARGS="--rm -d --name 'test_asr'" ./run_docker.sh test_config.yml
    waitalive docker logs test_asr '2>&1' '|' grep -q "'sample_rate: 16000'"
else
    ./run_whisper.sh -c test_config_local.yml >test.log 2>&1 || exit 1&
    waitalive grep -q "'sample_rate: 16000'" test.log
    rm test.log
fi
# cp play_the_next_song.wav ./audio/   # now committed in git
uv run tester.py
