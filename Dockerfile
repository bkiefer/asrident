FROM mypy:3.11

WORKDIR /app
RUN git clone https://github.com/bkiefer/asrident.git
WORKDIR /app/asrident
RUN git pull --recurse-submodules
RUN git submodule update --init --recursive --remote
RUN uv sync
RUN uv pip install -e ./whisper-gstreamer