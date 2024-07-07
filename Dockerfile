FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/London

# Update package list and install dependencies
RUN apt-get -y update && \
    apt-get -y install cron locales git python3-dev python3-pip
#         # requirements
#         ffmpeg \
#         python3-dev \
#         python3-pip\
#         git \
#         locales \
#         cron \
#         # subaligner
#         espeak \
#         libespeak1 \
#         libespeak-dev \
#         espeak-data \
#         libsndfile-dev \
#         libhdf5-dev \
#         python3-tk \
#         # subsync
#         python3-pybind11 \
#         libsphinxbase-dev \
#         libpocketsphinx-dev \
#         libavdevice-dev \
#         libavformat-dev \
#         libavfilter-dev \
#         libavcodec-dev \
#         libswresample-dev \
#         libswscale-dev \
#         libavutil-dev && \
#     apt-get -y clean

# RUN python3 -m pip install --upgrade pip && \
#     python3 -m pip install --upgrade setuptools wheel

RUN locale-gen "en_US.UTF-8"
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# WORKDIR /opt/subaligner
# RUN git clone https://github.com/baxtree/subaligner.git . && \
#     pip install -r requirements.txt && pip install -r requirements-stretch.txt && \
#     python3 -m pip install . && \
#     python3 -m pip install "subaligner[harmony]"

# WORKDIR /opt/subsync
# RUN git clone https://github.com/sc0ty/subsync.git . && \
#     cp subsync/config.py.template subsync/config.py && \
#     # mkdir /config && chmod 777 /config && \
#     pip install -r requirements.txt && \
#     pip install .

# WORKDIR /opt/subcleaner
# RUN git clone https://github.com/KBlixt/subcleaner.git . && \
#     python3 ./subcleaner.py -h

WORKDIR /opt/subaligner-bazarr
RUN git clone https://github.com/Tarzoq/subaligner-bazarr.git . && \
    pip install -r requirements.txt && \
    touch /var/log/cron.log && \
    chmod +x /opt/subaligner-bazarr/start.sh

# Clean up unnecessary files to reduce image size
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Optionally, set the working directory
WORKDIR /working
CMD ["/opt/subaligner-bazarr/start.sh"]