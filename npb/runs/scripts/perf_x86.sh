#!/bin/bash

# Parameters
experiment=$1
baseline=$2
class=$3
skip_baseline=$4

# Setup
echo "====================[ Setting up the experiment ]===================="
source ../../venv/bin/activate || exit 1
export NPB_PATH=/home/nikos/phd/unified_abi/layout/npb

echo "====================[ Setting governor to \"performance\"]===================="
for i in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
do
  sudo bash -c "echo performance >$i"
done

if [ -z ${skip_baseline} ]; then
  # Baseline experiment
  echo "====================[ Running the baseline experiment ]===================="
  npb \
      --config configs/performance-regression/o1/${baseline}/nettuno/build_run_x86.json \
      --dest experiments/performance-regression/o1/${baseline}/nettuno \
      --npb-class ${class} \
      --build \
      --run \
      --post-process || exit 1
fi

# Regression experiment
echo "====================[ Running the regression experiment ]===================="
npb \
    --config configs/performance-regression/o1/${experiment}/nettuno/build_run_x86.json \
    --dest experiments/performance-regression/o1/${experiment}/nettuno \
    --npb-class ${class} \
    --build \
    --run \
    --post-process || exit 1

# Compare experiments
echo "====================[ Comparing the experiments ]===================="
npb \
    --config configs/performance-regression/o1/${experiment}/nettuno/build_run_x86.json \
    --dest experiments/performance-regression/o1/${experiment}/nettuno \
    --compare /home/nikos/phd/unified_abi/npb/runs/experiments/performance-regression/o1/${baseline}/nettuno/run \
    --npb-class ${class} || exit 1

# Revert governor to "ondemand"
echo "====================[ Reverting governor to \"ondemand\"]===================="
for i in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
do
  sudo bash -c "echo ondemand >$i"
done