#!/bin/bash

cmd1="python3.7 -m spec2017.run_spec --config-list spec2017/config/clang_base.cfg --threads=1 --bench=600,602,605,625 --iterations=3 --noreportable --tune=base"
cmd2="python3.7 -m spec2017.run_spec --config-list spec2017/config/base.cfg --full-thread-run --bench  600 602 605 625 657 --noreportable"

if [ "$1" = "preview" ]; then
	cmd1+=" --preview"
	cmd2+=" --preview"
	shift
fi

for short_hash in "$@"
do
  echo "Experiment: $short_hash"
  echo "Result Directory: ${SPEC_SCRIPT_DIR}/results/${short_hash}"

  export PATH=~/my_llvm/toolchain_exp/bin/:$PATH
  export LD_LIBRARY_PATH=$(llvm-config --libdir)
  export SPEC_DIR=/home/nikos/cpu2017
  export SPEC_RESULT_DIR=${SPEC_SCRIPT_DIR}/results/${short_hash}

  git checkout "$short_hash"

  cp "${SPEC_SCRIPT_DIR}"/config/clang_base.cfg "${SPEC_DIR}"/config/spec2017/config
  if [ ! -d "$SPEC_RESULT_DIR" ];then
    echo
    mkdir "$SPEC_RESULT_DIR"
  fi

  cp "${SPEC_SCRIPT_DIR}"/config/info.json "${SPEC_RESULT_DIR}"

  sudo -E bash -c "$cmd1"
  # TODO does not work for multithread runs
  EXPERIMENT_NUM=$(awk '{print $1; exit}' "$SPEC_DIR"/result/lock.CPU2017)
  cp "$SPEC_DIR"/result/CPU2017."$EXPERIMENT_NUM".log "$SPEC_RESULT_DIR"
  cp "$SPEC_DIR"/result/CPU2017."$EXPERIMENT_NUM".intspeed.refspeed.csv "$SPEC_RESULT_DIR"

  #bash -c "$cmd2"
  #EXPERIMENT_NUM=$(awk '{print $1; exit}' "$SPEC_DIR"/result/lock.CPU2017)
  #cp "$SPEC_DIR"/result/CPU2017."$EXPERIMENT_NUM".log "$SPEC_RESULT_DIR"

done
git checkout development
