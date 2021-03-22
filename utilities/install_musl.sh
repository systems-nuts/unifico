#!/bin/bash

cd ~/popcorn-compiler/lib/musl-1.1.18

rm -rf build_x86-64 build_aarch64 toolchain_x86-64 toolchain_aarch64
mkdir build_x86-64 build_aarch64 toolchain_x86-64 toolchain_aarch64

cd build_x86-64
../configure --prefix=$(pwd)/../toolchain_x86-64 --target=x86_64-linux-gnu --enable-optimize --enable-debug --enable-warnings --enable-wrapper=all --disable-shared CC=/home/nikos/llvm_9/toolchain/bin/clang CFLAGS="-target x86_64-linux-gnu -popcorn-alignment -ffunction-sections -fdata-sections" KERVER=POPCORN_5_2
make -j16
make install

cd ../build_aarch64
../configure --prefix=$(pwd)/../toolchain_aarch64 --target=aarch64-linux-gnu --enable-optimize --enable-debug --enable-warnings --enable-wrapper=all --disable-shared CC=/home/nikos/llvm_9/toolchain/bin/clang CFLAGS="-target aarch64-linux-gnu -popcorn-alignment -ffunction-sections -fdata-sections" KERVER=POPCORN_5_2
make -j16
make install
