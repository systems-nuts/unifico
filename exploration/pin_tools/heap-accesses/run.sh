#! /bin/bash

#cd ~/Documents/phd/unified_abi/layout/call-leaf || exit
#make clean && make init
/opt/pin-3.20-98437-gf02b61307-gcc-linux/pin -t obj-intel64/heap_accesses.so -o temp.txt -- /home/blackgeorge/CLionProjects/DAMOV/workloads/ligra/apps/Triangle /home/blackgeorge/CLionProjects/DAMOV/workloads/ligra/inputs/rMatGraph_J_5_100
