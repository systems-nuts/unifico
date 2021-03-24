#!/bin/bash

make clean
make check
gdb -q call_leaf_x86_64_aligned.out -x gdb_call_leaf
