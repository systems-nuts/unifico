#!/bin/bash

class=$1
iterations=$2
commit_hashes="${@:3}"

echo "Running NPB for Class $class"

for hash in $commit_hashes; do

	echo "Running hash: $hash"

	# Build LLVM source
	./build-llvm-from-hash.sh $hash

	# Build NPB
	make clean
	make $class
	make init

	# Run on x64 machine
	./run.sh $hash $class x86_64 init $iterations

	# Run on arm machine
	./run-from-hash-sole.sh $hash $class init $iterations
done

