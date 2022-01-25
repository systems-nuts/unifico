#!/bin/bash


for filename in *.s; do
	diff $filename $1 >/dev/null
	if [[ $? -eq 1 ]] 
	then
		echo $filename
	fi
done
