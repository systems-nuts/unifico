#!/bin/bash

benchmarks="bt cg dc ep ft is lu mg sp ua"
x86_dir="assembly-files/x86-64"
arm_dir="assembly-files/aarch64"

rm -rf assembly-files/*
mkdir -p $x86_dir $arm_dir

for bench in $benchmarks
do
	echo $bench
	mkdir -p $x86_dir/$bench
	mkdir -p $arm_dir/$bench
	cp $bench/build_x86-64/*.s $x86_dir/$bench
	cp $bench/build_aarch64/*.s $arm_dir/$bench
done
