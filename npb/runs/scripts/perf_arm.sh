#!/bin/bash

# Parameters
experiment=$1
baseline=$2
class=$3
skip_baseline=$4

# Setup
echo "====================[ Setting up the experiment ]===================="
source ../../venv/bin/activate || exit 1

# Baseline experiment
if [ -z ${skip_baseline} ]; then
  echo "====================[ Running the baseline experiment ]===================="
  python npb_run.py \
      --config configs/performance-regression/o1/${baseline}/sole/build_run_arm.json \
      --dest experiments/performance-regression/o1/${baseline}/sole \
      --npb-class ${class} \
      --build \
      --run \
      --post-process || exit 1
fi

# Regression experiment
echo "====================[ Running the regression experiment ]===================="
python npb_run.py \
    --config configs/performance-regression/o1/${experiment}/sole/build_run_arm.json \
    --dest experiments/performance-regression/o1/${experiment}/sole \
    --npb-class ${class} \
    --build \
    --run \
    --post-process || exit 1

# Compare experiments
echo "====================[ Comparing the experiments ]===================="
python npb_run.py \
    --config configs/performance-regression/o1/${experiment}/sole/build_run_arm.json \
    --dest experiments/performance-regression/o1/${experiment}/sole \
    --compare /code/unifico-cc24/npb/runs/experiments/performance-regression/o1/${baseline}/sole/run \
    --npb-class ${class} || exit 1
