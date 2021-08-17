#!/bin/sh

experiment_name=$1
class=$2
arch=$3

mkdir -p bin
mkdir -p result/${experiment_name}

for benchmark in dc ft mg cg lu bt is ep sp ua; do

	bin=${benchmark}/${benchmark}_${arch}_unaligned.out

	for iteration in 1 2 3; do

		out_file=${benchmark}.${arch}.${class}.${iteration}.out
		echo "Running ${bin}, result to ${out_file}"	
		${bin} >result/${experiment_name}/${out_file}

	done
done

echo "Done.\n"
