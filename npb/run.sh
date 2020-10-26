#!/bin/bash

for short_hash in "$@"
do
  echo "Experiment: $short_hash"
  echo "Result Directory: ${NPB_SCRIPT_DIR}/results/${short_hash}"
  export NPB_RESULT_DIR=${NPB_SCRIPT_DIR}/results/${short_hash}
  if [ ! -d "$NPB_RESULT_DIR" ];then
    echo
    mkdir "$NPB_RESULT_DIR"
  fi
  sudo -E bash -c "python3.7 -m unified_abi.npb.run_npb --suite-list test_suite.def --full-core-run --iterations=3 --preview"
  sudo -E bash -c "python3.7 -m unified_abi.npb.run_npb --suite-list test_suite.def --full-thread-run --iterations=3 --preview"

done