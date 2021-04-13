#!/bin/bash

make clean
make check
make assembly
gdb -q call_leaf_x86_64_aligned.out -x gdb_call_leaf
