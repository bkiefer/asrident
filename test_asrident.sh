#!/bin/sh
DOCKER_ARGS="--rm -d --name 'test_asr'" ./run_docker.sh test_config.yml
until docker logs test_asr 2>&1 | grep -q 'sample_rate: 16000'; do
    sleep 3
done
cp play_the_next_song.wav ./audio/
uv run tester.py
