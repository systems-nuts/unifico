#!/bin/bash

cmd1="python3.7 -m spec2017.run_spec --config-list spec2017/config/clang_base.cfg --threads=1 \
      --bench=600,602,605,625 --iterations=3 --noreportable --tune=base"
cmd2="python3.7 -m spec2017.run_spec --config-list spec2017/config/clang_base.cfg --full-core-run \
      --bench 657 --noreportable"
cmd3="python3.7 -m spec2017.run_spec --config-list spec2017/config/clang_base.cfg --full-thread-run \
      --bench 657 --noreportable"

if [ "$1" = "preview" ]; then
	cmd1+=" --preview"
	cmd2+=" --preview"
	cmd3+=" --preview"
	shift
fi

for short_hash in "$@"
do
  echo "==============================================="

  export PATH=~/toolchain1/bin/:$PATH
  export LD_LIBRARY_PATH=$(llvm-config --libdir)
  export SPEC_DIR=/home/nikos/cpu2017
  export RESULT_DIR=${SPEC_SCRIPT_DIR}/results/${short_hash}_base

  git checkout "$short_hash"

  cp "${SPEC_SCRIPT_DIR}"/config/clang_base.cfg "${SPEC_DIR}"/config/spec2017/config

  if [ ! -d "$RESULT_DIR" ];then
    echo
    mkdir "$RESULT_DIR"
  fi
  cp "${SPEC_SCRIPT_DIR}"/config/info.json "${RESULT_DIR}"

  sudo -E bash -c "$cmd1"
  # SPEC auto increment number after one serial experiments
  FIRST_EXP_NUM=$(awk '{print $1; exit}' "$SPEC_DIR"/result/lock.CPU2017)
  cp "$SPEC_DIR"/result/CPU2017."$FIRST_EXP_NUM".intspeed.refspeed.csv "$RESULT_DIR"

  sudo -E bash -c "$cmd2"
  CORE_EXP_RESULT_DIR="$RESULT_DIR"/core_run
  if [ ! -d "$CORE_EXP_RESULT_DIR" ];then
    echo
    mkdir "CORE_EXP_RESULT_DIR"
  fi
  # SPEC auto increment number after some compact affinity experiments
  SECOND_EXP_NUM=$(awk '{print $1; exit}' "$SPEC_DIR"/result/lock.CPU2017)
  for ((i=FIRST_RESULT_NUM+1;i<=SECOND_EXP_NUM;i++))
  do
    cp "$SPEC_DIR"/result/CPU2017.$i.intspeed.refspeed.csv "$CORE_EXP_RESULT_DIR"
  done

 sudo -E bash -c "$cmd3"
  THREAD_EXP_RESULT_DIR="$RESULT_DIR"/thread_run
  if [ ! -d "$THREAD_EXP_RESULT_DIR" ];then
    echo
    mkdir "THREAD_EXP_RESULT_DIR"
  fi
  # SPEC auto increment number after some scatter affinity experiments
  THIRD_EXP_NUM=$(awk '{print $1; exit}' "$SPEC_DIR"/result/lock.CPU2017)
  for ((i=SECOND_EXP_NUM+1;i<=THIRD_EXP_NUM;i++))
  do
    cp "$SPEC_DIR"/result/CPU2017.$i.intspeed.refspeed.csv "$THREAD_EXP_RESULT_DIR"
  done

echo "==============================================="
done
git checkout development
