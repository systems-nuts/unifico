#!/bin/bash

OPT_FLAGS_FILE=opt_O1.txt

flags=$(<$OPT_FLAGS_FILE)

cd call_leaf || exit 1
rm *.s

for flag in $flags
do
	make clean; make OPT_FLAGS=${flag:1}
	echo '================'
done
