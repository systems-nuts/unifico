#!/bin/bash

make clean
make check
make asm
gdb -q call_leaf_x86_64_aligned.out -x gdb_call_leaf

if [ $# -ne 0 ]; then
	scp call_leaf_aarch64_aligned.out nikos@sole:~/phd/unified_abi/layout/call_leaf
fi
