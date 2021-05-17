#!/bin/bash

make clean
make check
make asm
gdb -q bubble_sort_x86_64_aligned.out -x gdb_bubble_sort

if [ $# -ne 0 ]; then
	scp bubble_sort_aarch64_aligned.out nikos@sole:~/phd/unified_abi/layout/bubble_sort
fi
