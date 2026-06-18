#!/bin/sh
if docker images 2>&1 | grep -q asrident; then
    DOCKER_ARGS="--rm -d --name 'test_asr'" ./run_docker.sh test_config.yml
    until docker logs test_asr 2>&1 | grep -q 'sample_rate: 16000'; do
        sleep 3
    done
else
    ./run_whisper.sh -c test_config_local.yml >test.log 2>&1 &
    until grep -q 'sample_rate: 16000' test.log; do
        sleep 3
    done
fi
# cp play_the_next_song.wav ./audio/   # now committed in git
uv run tester.py
