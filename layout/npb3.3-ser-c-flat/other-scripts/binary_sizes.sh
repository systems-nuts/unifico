#!/bin/bash

benchmarks="bt cg dc ep ft is lu mg sp ua"

rm unasl-sizes/*

for bench in $benchmarks
do
	echo $bench/${bench}_x86_64_aligned.out 
	size -Ad $bench/${bench}_x86_64_aligned.out >unasl-sizes/${bench}.txt
	#size -Ad $bench/${bench}_aarch64_aligned.out >sizes/${bench}_aarch64.txt
done
