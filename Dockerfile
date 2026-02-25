FROM mypy:3.11

WORKDIR /app
RUN git init
RUN git remote add origin https://github.com/bkiefer/asrident.git
RUN git fetch
RUN git checkout -t origin/drz
RUN git pull --recurse-submodules
RUN git submodule update --init --recursive --remote
RUN uv sync
RUN uv pip install -e ./whisper-gstreamer