#!/bin/bash

make clean
make c f
gdb -q call_leaf_2.out -x gdb_call_leaf
gdb -q fact_2.out -x gdb_fact
