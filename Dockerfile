FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/London

# Update package list and install dependencies
RUN apt-get -y update && \
    apt-get -y install \
        # requirements
        ffmpeg \
        python3-dev \
        python3-pip\
        git \
        locales \
        nano \
        cron \
        # subaligner
        espeak \
        libespeak1 \
        libespeak-dev \
        espeak-data \
        libsndfile-dev \
        libhdf5-dev \
        python3-tk \
        # subsync
        python3-pybind11 \
        libsphinxbase-dev \
        libpocketsphinx-dev \
        libavdevice-dev \
        libavformat-dev \
        libavfilter-dev \
        libavcodec-dev \
        libswresample-dev \
        libswscale-dev \
        libavutil-dev && \
    apt-get -y clean && \
    # python3
    python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade setuptools wheel && \
    # locale
    locale-gen "en_US.UTF-8"

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

RUN mkdir "/opt/subaligner" && cd "/opt/subaligner" && \
    # subaligner
    git clone https://github.com/baxtree/subaligner.git . && \
    pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir -r requirements-stretch.txt && \
    python3 -m pip install --no-cache-dir . && \
    python3 -m pip install --no-cache-dir "subaligner[harmony]" && \
    mkdir "/opt/subsync" && cd "/opt/subsync" && \
    # subsync
    git clone https://github.com/sc0ty/subsync.git . && \
    cp subsync/config.py.template subsync/config.py && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir . && \
    mkdir "/opt/subcleaner" && cd "/opt/subcleaner" && \
    # subcleaner
    git clone https://github.com/KBlixt/subcleaner.git . && \
    python3 ./subcleaner.py -h && \
    mkdir "/opt/subaligner-bazarr" && cd "/opt/subaligner-bazarr" && \
    # subaligner-bazarr
    git clone https://github.com/Tarzoq/subaligner-bazarr.git . && \
    pip install --no-cache-dir -r requirements.txt && \
    chmod +x /opt/subaligner-bazarr/start.py && \
    # Clean up unnecessary files to reduce image size
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /working
CMD ["python3", "-u", "/opt/subaligner-bazarr/start.py"]