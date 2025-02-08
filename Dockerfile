FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV TZ=UTC

# Update package list and install dependencies
RUN apt-get -y update && \
    apt-get -y install \
        # requirements
        python3-dev \
        python3-pip\
        git \
        locales \
        nano \
        cron \
        # subsync
        python3-pybind11 \
        ffmpeg \
        libsphinxbase-dev \
        libpocketsphinx-dev \
        libavdevice-dev \
        libavformat-dev \
        libavfilter-dev \
        libavcodec-dev \
        libswresample-dev \
        libswscale-dev \
        libavutil-dev \
        libportaudio2 && \
    apt-get -y clean && \
    # python3
    pip3 install --no-cache-dir --upgrade pip setuptools wheel pipreqs && \
    # locale
    locale-gen "en_US.UTF-8"

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

RUN mkdir "/opt/subsync" && cd "/opt/subsync" && \
    # subsync
    git clone https://github.com/sc0ty/subsync.git . && \
    cp subsync/config.py.template subsync/config.py && \
    pip3 install --no-cache-dir -r requirements.txt && \
    pip3 install --no-cache-dir . && \
    mkdir "/opt/subsyncerr" && cd "/opt/subsyncerr" && \
    # subsyncerr
    git clone https://github.com/Tarzoq/subsyncerr.git . && \
    pip install --no-cache-dir -r requirements.txt && \
    chmod +x /opt/subsyncerr/start.py && \
    mkdir "/opt/srt-lang-detect" && cd "/opt/srt-lang-detect" && \
    # srt-lang-detect
    git clone https://github.com/mdcollins05/srt-lang-detect.git . && \
    pipreqs && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir "/opt/subcleaner" && cd "/opt/subcleaner" && \
    # subcleaner
    git clone https://github.com/KBlixt/subcleaner.git . && \
    python3 ./subcleaner.py -h && \
    # Clean up unnecessary files to reduce image size
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /working
CMD ["python3", "-u", "/opt/subsyncerr/start.py"]