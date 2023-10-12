#!/bin/bash

# Parameters
experiment=$1
baseline=$2
class=$3

# Setup
echo "====================[ Setting up the experiment ]===================="
source ../../venv/bin/activate || exit 1
export NPB_PATH=/home/nikos/phd/unified_abi/layout/npb

# Baseline experiment
echo "====================[ Running the baseline experiment ]===================="
npb \
    --config configs/performance-regression/o1/${baseline}/sole/build_run_arm.json \
    --dest experiments/performance-regression/o1/${baseline}/sole \
    --npb-class ${class} \
    --build \
    --run \
    --post-process || exit 1

# Regression experiment
echo "====================[ Running the regression experiment ]===================="
npb \
    --config configs/performance-regression/o1/${experiment}/sole/build_run_arm.json \
    --dest experiments/performance-regression/o1/${experiment}/sole \
    --npb-class ${class} \
    --build \
    --run \
    --post-process || exit 1

# Compare experiments
echo "====================[ Comparing the experiments ]===================="
npb \
    --config configs/performance-regression/o1/${experiment}/sole/build_run_arm.json \
    --dest experiments/performance-regression/o1/${experiment}/sole \
    --compare /home/nikos/phd/unified_abi/npb/runs/experiments/performance-regression/o1/${baseline}/sole/run \
    --npb-class ${class} || exit 1
