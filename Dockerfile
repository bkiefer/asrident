FROM ubuntu:25.04

ENV TZ=Europe/Berlin
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -q -qq update && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends \
    libgstreamer1.0-dev \
    gstreamer1.0-alsa \
    gstreamer1.0-pulseaudio \
    ffmpeg \
    python3-pip \
    python3-cairo \
    python3-gst-1.0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app
RUN pip3 install --break-system-packages -r /app/requirements.txt
RUN rm -rf /root/.cache/pip

COPY whisper-gstreamer/src/transcriptor.py /app
COPY whisper-gstreamer/src/vad_iterator.py /app
COPY whisper-gstreamer/src/gstmicpipeline.py /app
COPY transpeak.py /app
COPY spkident.py /app
COPY run_whisper.sh /app
