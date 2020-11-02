#!/bin/bash

cmd1="python3.7 -m npb.run_npb --suite-list suite.def --full-core-run --iterations=3"
cmd2="python3.7 -m npb.run_npb --suite-list suite.def --full-thread-run --iterations=3"

if [ $1 = "preview" ]; then
	cmd1+=" --preview"
	cmd2+=" --preview"
	shift
fi

for short_hash in "$@"
do
  echo "Experiment: $short_hash"
  echo "Result Directory: ${NPB_SCRIPT_DIR}/results/${short_hash}"

  export NPB_RESULT_DIR=${NPB_SCRIPT_DIR}/results/${short_hash}

  git checkout "$short_hash"

  cp "${NPB_SCRIPT_DIR}"/config/make.def "${NPB_DIR}"/config
  cp "${NPB_SCRIPT_DIR}"/config/suite.def "${NPB_DIR}"/config
  if [ ! -d "$NPB_RESULT_DIR" ];then
    echo
    mkdir "$NPB_RESULT_DIR"
  fi

  bash -c "$cmd1"
  bash -c "$cmd2"

done
git checkout npb_experiments
