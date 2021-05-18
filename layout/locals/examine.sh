#!/bin/bash

make clean
make check
make asm
gdb -q locals_x86_64_aligned.out -x gdb_locals

if [ $# -ne 0 ]; then
	scp locals_aarch64_aligned.out nikos@sole:~/phd/unified_abi/layout/locals
fi
