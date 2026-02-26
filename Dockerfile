FROM mypy:3.11

WORKDIR /app
COPY whisper-gstreamer/pyproject.toml /app/whisper-gstreamer/pyproject.toml
COPY whisper-gstreamer/src /app/whisper-gstreamer/src
COPY pyproject.toml transpeak.py spkident.py run_whisper.sh /app
COPY mqttrecorder.py /app
RUN uv sync
RUN uv pip install -e ./whisper-gstreamer