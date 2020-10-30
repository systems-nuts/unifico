#!/bin/bash

for short_hash in "$@"
do
  echo "Experiment: $short_hash"
  sudo -E bash -c "python3.7 -m spec2017.run_spec --config-list spec2017/config/baseline_gcc.cfg --full-core-run --bench 657 --noreportable"
  sudo -E bash -c "python3.7 -m spec2017.run_spec --config-list spec2017/config/baseline_gcc.cfg --full-thread-run --bench 657 --noreportable"
done
