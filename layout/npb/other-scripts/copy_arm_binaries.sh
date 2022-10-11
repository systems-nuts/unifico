#!/bin/bash

for bench in bt cg dc ep ft is lu mg sp ua; do
	echo -n "Copying ${bench}... "
	sshpass -f sole.txt scp ${bench}/${bench}_aarch64_init.out nikos@sole:phd/unified_abi/layout/npb/${bench}
	echo "Done."
done
