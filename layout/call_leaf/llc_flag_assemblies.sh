#!/bin/bash

rm *.s

for regalloc in "basic" "fast" "greedy";do
	llc_flags=-regalloc=$regalloc
	for opt_flags in "" "-mem2reg";do
		echo $llc_flags
		echo $opt_flags
		make clean
		make OPT_FLAGS="$opt_flags" LLC_FLAGS="$llc_flags"
		gdb -q call_leaf.out -x ../gdb_call_leaf
	done
done
