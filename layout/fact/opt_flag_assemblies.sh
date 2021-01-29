#!/bin/bash

OPT_FLAGS_FILE=../opt_O1.txt

flags=$(<$OPT_FLAGS_FILE)

for flag in $flags
do
	make clean; make OPT_FLAGS="-mem2reg $flag" PREFIX=${flag:1}
	echo '================'
done
