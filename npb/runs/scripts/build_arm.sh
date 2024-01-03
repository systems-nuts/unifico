#!/bin/bash

# Parameters
experiment=$1
baseline=$2
class=$3
skip_baseline=$4

# Setup
echo "====================[ Setting up the experiment ]===================="
source ../../venv/bin/activate || exit 1

# Build arm
if [ -z ${skip_baseline} ]; then
  echo "====================[ Building the arm baseline experiment ]===================="
  python npb_run.py \
      --config configs/performance-regression/o1/${baseline}/nettuno/build_arm.json \
      --dest experiments/performance-regression/o1/${baseline}/sole \
      --npb-class ${class} \
      --build || exit 1
fi

# Build arm
echo "====================[ Building the arm regression experiment ]===================="
python npb_run.py \
    --config configs/performance-regression/o1/${experiment}/nettuno/build_arm.json \
    --dest experiments/performance-regression/o1/${experiment}/sole \
    --npb-class ${class} \
    --build || exit 1
