#! /bin/bash

cd ~/Documents/phd/unified_abi/layout/experimentation/array-write/ || exit
make clean && make init
cd - || exit
/opt/pin-3.20-98437-gf02b61307-gcc-linux/pin -t obj-intel64/heap_accesses.so -o heap_accesses.csv -f sort -- /home/blackgeorge/Documents/phd/unified_abi/layout/experimentation/array-write/main_x86_64_init.out
