#!/bin/bash

make clean
make check
make asm
gdb -q fact_x86_64_aligned.out -x gdb_fact

if [ $# -ne 0 ]; then
	scp fact_aarch64_aligned.out nikos@sole:~/phd/unified_abi/layout/fact
fi
