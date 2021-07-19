#!/bin/bash

make clean
make check
make asm
# gdb -q fact_x86_64_aligned.out -x gdb_fact
