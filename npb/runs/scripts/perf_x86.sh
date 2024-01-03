#!/bin/bash

# Parameters
experiment=$1
baseline=$2
class=$3
skip_baseline=$4

# Setup
echo "====================[ Setting up the experiment ]===================="
source ../../venv/bin/activate || exit 1

if [ -z ${skip_baseline} ]; then
  # Baseline experiment
  echo "====================[ Running the baseline experiment ]===================="
  python npb_run.py \
      --config configs/performance-regression/o1/${baseline}/nettuno/build_run_x86.json \
      --dest experiments/performance-regression/o1/${baseline}/nettuno \
      --npb-class ${class} \
      --build \
      --run \
      --post-process || exit 1
fi

# Regression experiment
echo "====================[ Running the regression experiment ]===================="
python npb_run.py \
    --config configs/performance-regression/o1/${experiment}/nettuno/build_run_x86.json \
    --dest experiments/performance-regression/o1/${experiment}/nettuno \
    --npb-class ${class} \
    --build \
    --run \
    --post-process || exit 1

# Compare experiments
echo "====================[ Comparing the experiments ]===================="
python npb_run.py \
    --config configs/performance-regression/o1/${experiment}/nettuno/build_run_x86.json \
    --dest experiments/performance-regression/o1/${experiment}/nettuno \
    --compare /code/unifico-cc24/npb/runs/experiments/performance-regression/o1/${baseline}/nettuno/run \
    --npb-class ${class} || exit 1
