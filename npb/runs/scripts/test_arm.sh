#!/bin/bash

experiment=$1

source ../../venv/bin/activate
export NPB_PATH=/home/nikos/phd/unified_abi/layout/npb
npb -c configs/performance-regression/o1/${experiment}/sole/build_run_arm.json -d experiments/performance-regression/o1/${experiment}/sole --npb-class S -b -r -p
