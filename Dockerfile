##
# Dockerfile for popcorn-compiler
#
# This file builds the popcorn-compiler for popcorn-kernel v5.2 using the
# Ubuntu18.04 as the base image.
#
# The clang/LLVM compiler lives at /usr/local/popcorn/bin/clang
# The musl wrapper for LLVM is at /usr/local/popcorn/x86_64/bin/musl-clang
# 
# Build application code (located in ./code):
# docker run --rm -v $(pwd)/app:/code/app <image id> make -C /code/app
##

FROM ubuntu:bionic
RUN apt-get update -y && apt-get install -y --no-install-recommends \
  bison cmake flex g++ gcc git zip make patch texinfo \
  python3 ca-certificates libelf-dev gcc-aarch64-linux-gnu locales vim
RUN apt-get install -y python-minimal 

# Set the locale
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

WORKDIR /code
RUN git clone https://github.com/ssrg-vt/popcorn-compiler

WORKDIR /code/popcorn-compiler
RUN git checkout criu
COPY install_compiler.py /code/popcorn-compiler
COPY gmo2msg.c /code/popcorn-compiler/lib/libelf/po/gmo2msg.c
COPY llvm-3.7.patch /code/popcorn-compiler/patches/llvm
RUN ./install_compiler.py --install-binutils && rm -rf /usr/local/popcorn/src
RUN ls /usr/local/popcorn/bin
# Install pyalign and check-align (`--install-tools` may fail but it's ok)
RUN ./install_compiler.py --install-utils --install-tools


# Fetch LLVM
WORKDIR /code
RUN git clone https://github.com/blackgeorge-boom/llvm-unifico

# Install musl
WORKDIR /code/llvm-unifico
RUN git checkout musl
WORKDIR /usr/local/llvm-9-align/build
WORKDIR /usr/local/llvm-9-align/toolchain
RUN cp /code/llvm-unifico/build_exp.sh /usr/local/llvm-9-align/build
WORKDIR /usr/local/llvm-9-align/build
RUN apt-get install ninja-build
RUN ./build_exp.sh && cmake --build . && ninja install

WORKDIR /code
RUN git clone https://github.com/systems-nuts/musl-stack-reloc.git
WORKDIR /code/musl-stack-reloc
RUN git checkout cc24-ae
RUN ./install_musl.sh -c /usr/local/llvm-9-align/toolchain -d /usr/local/musl-toolchains/unifico

# Install Unifico
WORKDIR /code/llvm-unifico
RUN git fetch && git checkout cc24-ae && git pull
WORKDIR /usr/local/llvm-9/build
WORKDIR /usr/local/llvm-9/toolchain
RUN cp /code/llvm-unifico/build_exp.sh /usr/local/llvm-9/build
WORKDIR /usr/local/llvm-9/build
RUN ./build_exp.sh && cmake --build . && ninja install

# Install Unifico tools
WORKDIR /code
RUN git clone https://github.com/blackgeorge-boom/unifico-cc24
WORKDIR /code/unifico-cc24
RUN apt-get -y install python3-venv python3-pip
RUN python3 -m venv venv
RUN python3 -m pip install --upgrade pip

# Set up python environment
RUN set -o vi
RUN apt-get -y install libjpeg-dev zlib1g
ENV NPB_PATH /code/unifico-cc24/layout/npb

WORKDIR /code/unifico-cc24/
RUN git pull && git checkout cc24-ae

# Install Unifico
WORKDIR /code/llvm-unifico
RUN git fetch && git checkout cc24-ae-vanilla && git pull
WORKDIR /usr/local/llvm-9.0.1/build
WORKDIR /usr/local/llvm-9.0.1/toolchain
RUN cp /code/llvm-unifico/build_exp.sh /usr/local/llvm-9.0.1/build
WORKDIR /usr/local/llvm-9.0.1/build
RUN ./build_exp.sh && cmake --build . && ninja install

WORKDIR /code/musl-stack-reloc
RUN git checkout unmodified
RUN ./install_musl.sh -c /usr/local/llvm-9.0.1/toolchain -d /usr/local/musl-toolchains/unmodified

WORKDIR /code/unifico-cc24/
RUN touch setup.cfg
RUN venv/bin/python -m pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install -e .
RUN rm setup.cfg
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && apt-get install -y texlive texlive-latex-extra texlive-fonts-recommended dvipng
RUN apt update && apt -y install cm-super
RUN pwd && git fetch && git checkout cc24-ae
RUN git pull && git pull

WORKDIR /code/unifico-cc24/
RUN rm -rf /usr/local/llvm-9-align
# signal 35 to trigger the migration
## kill -35 $(pidof <popcorn bin>)
#RUN ./install_compiler.py --install-migration --with-popcorn-kernel-5_2 --libmigration-type=signal_trigger
