#!/bin/bash

# Parameters
experiment=$1
class=$2

# Setup
echo "====================[ Setting up the experiment ]===================="
source ../../venv/bin/activate || exit 1
export NPB_PATH=/home/nikos/phd/unified_abi/layout/npb

# Build arm
echo "====================[ Building the arm baseline experiment ]===================="
npb \
    --config configs/performance-regression/o1/vanilla/nettuno/build_arm.json \
    --dest experiments/performance-regression/o1/vanilla/sole \
    --npb-class ${class} \
    --build || exit 1

# Build arm
echo "====================[ Building the arm regression experiment ]===================="
npb \
    --config configs/performance-regression/o1/${experiment}/nettuno/build_arm.json \
    --dest experiments/performance-regression/o1/${experiment}/sole \
    --npb-class ${class} \
    --build || exit 1
