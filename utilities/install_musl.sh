#!/bin/bash

#MUSL_SRC=~/musl-stack-reloc
MUSL_SRC=~/popcorn-compiler/lib/musl-1.1.18

TOOLCHAIN_NAME=llvm-9
DESTINATION_DIR=~/musl-toolchains/${TOOLCHAIN_NAME}
X86_TOOLCHAIN_DIR=${DESTINATION_DIR}/x86-64
ARM_TOOLCHAIN_DIR=${DESTINATION_DIR}/aarch64

LLVM_TOOLCHAIN=/home/nikos/llvm-9/toolchain
CFLAGS="-popcorn-alignment -ffunction-sections -fdata-sections -fomit-frame-pointer"
#CFLAGS=""

cd ${MUSL_SRC}

rm -rf build_aarch64 build_x86-64
mkdir -p build_x86-64 build_aarch64 ${X86_TOOLCHAIN_DIR} ${ARM_TOOLCHAIN_DIR}

cd build_x86-64
../configure --prefix=${X86_TOOLCHAIN_DIR} --target=x86_64-linux-gnu --enable-optimize --enable-debug --enable-warnings --enable-wrapper=all --disable-shared CC=${LLVM_TOOLCHAIN}/bin/clang CFLAGS="-target x86_64-linux-gnu ${CFLAGS}" KERVER=POPCORN_5_2
make -j16
make install

cd ../build_aarch64
../configure --prefix=${ARM_TOOLCHAIN_DIR} --target=aarch64-linux-gnu --enable-optimize --enable-debug --enable-warnings --enable-wrapper=all --disable-shared CC=${LLVM_TOOLCHAIN}/bin/clang CFLAGS="-target aarch64-linux-gnu ${CFLAGS}" KERVER=POPCORN_5_2
make -j16
make install
