#!/bin/bash

OPT_FLAGS_FILE=../opt_flags.txt

flags=$(<$OPT_FLAGS_FILE)
uniq_flags=$(echo "$flags" | tr ' ' '\n' | sort | uniq | xargs )
echo $uniq_flags

for flag in $uniq_flags
do
	make clean; make OPT_FLAGS="-mem2reg $flag" PREFIX=${flag:1}
	echo '================'
done
