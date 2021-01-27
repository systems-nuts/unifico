#!/bin/bash


for filename in *.s; do
	diff $filename ../call_leaf_2.s >/dev/null
	if [[ $? -eq 1 ]] 
	then
		echo $filename
	fi
done
