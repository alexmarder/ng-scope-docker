FROM ubuntu:jammy

ARG DEBIAN_FRONTEND=noninteractive
ARG TZ=Etc/UTC

## Install dependencies
#RUN apt update -y
#RUN apt install -y build-essential cmake libfftw3-dev libmbedtls-dev libboost-program-options-dev libconfig++-dev libsctp-dev git nano python3-pip
#RUN pip3 install libconf
## Install USRP drivers
## TODO: Add option to choose the driver version
#RUN apt install -y libuhd-dev uhd-host

RUN apt-get update
#RUN apt-get upgrade -y
RUN apt-get install -y build-essential software-properties-common git cmake libfftw3-dev libmbedtls-dev libboost-program-options-dev libconfig++-dev libsctp-dev python3 python3-pip nano

RUN add-apt-repository ppa:ettusresearch/uhd
RUN apt-get update
RUN apt-get install -y libuhd-dev uhd-host
RUN uhd_images_downloader


# Install libasn
RUN git clone https://github.com/j0lama/libasn.git
WORKDIR libasn
RUN make -j$(nproc)
RUN make install
WORKDIR ../

# Download USRP images
RUN /usr/lib/uhd/utils/uhd_images_downloader.py

# Build ng-scope
RUN git clone https://github.com/YaxiongXiePrinceton/NG-Scope ng-scope
WORKDIR ng-scope/build
RUN cmake ../
RUN make -j$(nproc)
WORKDIR ngscope/src/logs
