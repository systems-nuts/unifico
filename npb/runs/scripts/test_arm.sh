#!/bin/bash

experiment=$1

# Setup
echo "====================[ Setting up the experiment ]===================="
source ../../venv/bin/activate || exit 1
export NPB_PATH=/home/nikos/phd/unified_abi/layout/npb

# Test experiment
echo "====================[ Running the test experiment ]===================="
npb \
    --config configs/performance-regression/o1/${experiment}/sole/build_run_arm.json \
    --dest experiments/performance-regression/o1/${experiment}/sole \
    --npb-class S \
    --build \
    --run \
    --post-process || exit 1
