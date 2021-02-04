#!/bin/bash

make clean
make aligned
gdb -q call_leaf_x86-64 -x gdb_call_leaf
