#!/bin/bash

if [ $# -ne 1 ]; then
	echo "Usage: $0 {S | A | B}"
	exit 1
fi

if [[ $1 != "S" && $1 != "A" && $1 != "B" ]]; then
	echo "Usage: $0 {S | A | B}"
	exit 1
fi

for W in bt cg dc ep ft is lu mg sp ua; do
	cd $W
	rm -f npbparams.h
	ln -s npbparams-$1.h npbparams.h
	cd ..
done
