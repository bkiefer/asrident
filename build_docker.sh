#!/bin/bash

cd whisper-gstreamer
. utils.sh
docker build -f Dockerfile_mypy3_11 -t mypy:3.11 .
cd ..

version=`grep version pyproject.toml | sed 's/version *= *"\([^"]*\)".*/\1/'`
docker build -f Dockerfile -t "$(getimage)" .
