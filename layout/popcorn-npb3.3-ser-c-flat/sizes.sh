#!/bin/bash

dest=$1

for npb in bt cg ep ft is lu mg sp ua; do
	size -A -d ${npb}/${npb}_x86-64 >${dest}/${npb}.txt
done
