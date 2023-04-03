#!/bin/bash

make clean
make check
make asm
gdb -q self-dump_x86_64_aligned.out -x gdb_main

if [ $# -ne 0 ]; then
	sshpass -p "nikos" scp -p self-dump_aarch64_aligned.out nikos@sole:~/phd/unified_abi/layout/test_reloc
fi
