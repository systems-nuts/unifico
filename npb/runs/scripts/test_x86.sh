#!/bin/bash

experiment=$1

# Setup
echo "====================[ Setting up the experiment ]===================="
source ../../venv/bin/activate || exit 1
export NPB_PATH=/home/nikos/phd/unified_abi/layout/npb

# Build arm
echo "====================[ Building the arm test experiment ]===================="
npb \
    --config configs/performance-regression/o1/${experiment}/nettuno/build_arm.json \
    --dest experiments/performance-regression/o1/${experiment}/sole \
    --npb-class S \
    --build || exit 1

# Regression experiment
echo "====================[ Running the test experiment ]===================="
npb \
    --config configs/performance-regression/o1/${experiment}/nettuno/build_run_x86.json \
    --dest experiments/performance-regression/o1/${experiment}/nettuno \
    --npb-class S \
    --build \
    --run \
    --post-process || exit 1
