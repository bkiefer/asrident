#!/bin/bash
uv sync
git submodule update --init --recursive --remote
git pull --recurse-submodules
uv pip install -e whisper-gstreamer
