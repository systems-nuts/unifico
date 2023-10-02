#!/bin/bash

experiment=$1

for i in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
do
  sudo bash -c "echo performance >$i"
done

source ../../venv/bin/activate
export NPB_PATH=/home/nikos/phd/unified_abi/layout/npb
npb -c configs/performance-regression/o1/${experiment}/nettuno/build_arm.json -d experiments/performance-regression/o1/${experiment}/sole --npb-class S -b
npb -c configs/performance-regression/o1/${experiment}/nettuno/build_run_x86.json -d experiments/performance-regression/o1/${experiment}/nettuno --npb-class S -b -r -p

for i in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
do
  sudo bash -c "echo ondemand >$i"
done