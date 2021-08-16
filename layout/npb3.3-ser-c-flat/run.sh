#!/bin/sh

mkdir -p bin
mkdir -p result

class=$1
arch=$2

for benchmark in dc ft mg cg lu bt is ep sp ua; do
	bin=${benchmark}/${benchmark}_${arch}_unaligned.out
	out_file=${benchmark}.${arch}.${class}.out

	echo "Running ${bin}, result to ${out_file}"	
	${bin} >result/${out_file}
done
echo "Done.\n"
