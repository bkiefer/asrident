#!/bin/bash

docker build -f whisper-gstreamer/Dockerfile_mypy3_11 -t mypy:3.11 .

version=`grep version pyproject.toml | sed 's/version *= *"\([^"]*\)".*/\1/'`
docker build -f Dockerfile -t asrident:"$version" .
