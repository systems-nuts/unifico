#!/bin/bash

cmd1="python3.7 -m spec2017.run_spec --config-list spec2017/config/clang_modified.cfg --threads=1 \
      --bench=600,602,605,625 --iterations=3 --noreportable --tune=base -i test,train,refspeed"
cmd2="python3.7 -m spec2017.run_spec --config-list spec2017/config/clang_modified.cfg \
      --threads=1,2,4,6,8 --bench 657 --iterations=3 --noreportable --tune=base -i test,train,refspeed"
cmd3="python3.7 -m spec2017.run_spec --config-list spec2017/config/clang_modified.cfg --full-thread-run \
      --bench 657 --iterations=3 --noreportable --tune=base -i test,train,refspeed"

if [ "$1" = "preview" ]; then
	cmd1+=" --preview"
	cmd2+=" --preview"
	cmd3+=" --preview"
	shift
fi

echo "Give pass:"
read -s PW
	
for short_hash in "$@"
do
  echo "==============================================="

  export PATH=~/my_llvm/toolchain/bin/:$PATH
  export AARCH64_TARGET=~/llvm-project/llvm/lib/Target/AArch64
  export BUILD_PATH=~/my_llvm/build
  export LD_LIBRARY_PATH=$(llvm-config --libdir)
  export SPEC_DIR=/home/nikos/cpu2017

  git checkout "$short_hash" -- spec2017/config/clang_modified.cfg spec2017/config/info.json spec2017/config/aarch64.patch

  # Apply changes to LLVM Target
  cd "$AARCH64_TARGET" || exit
  git apply -- "${SPEC_SCRIPT_DIR}"/config/aarch64.patch
  cd "$BUILD_PATH" || exit
  ./build_exp.sh
  cmake --build .
  ninja install

  cd "$SPEC_SCRIPT_DIR" || exit
  cd .. || exit

  # First Experiment
  cp "${SPEC_SCRIPT_DIR}"/config/clang_modified.cfg "${SPEC_DIR}"/config/spec2017/config
  echo $PW | sudo -S -E bash -c "$cmd1"

  # SPEC auto increment number after one serial experiments
  FIRST_EXP_NUM=$(awk '{print $1; exit}' "$SPEC_DIR"/result/lock.CPU2017)
  export RESULT_DIR=${SPEC_SCRIPT_DIR}/results/${FIRST_EXP_NUM}_${short_hash}
  if [ ! -d "$RESULT_DIR" ];then
    echo
    mkdir "$RESULT_DIR"
  fi

  # First Experiment Results
  cp "$SPEC_DIR"/result/CPU2017."$FIRST_EXP_NUM".intspeed.refspeed.csv "$RESULT_DIR"
  cp "${SPEC_SCRIPT_DIR}"/config/info.json "${RESULT_DIR}"

  # Second Experiment
  echo $PW | sudo -S -E bash -c "$cmd2"

  # SPEC auto increment number after some compact affinity experiments
  SECOND_EXP_NUM=$(awk '{print $1; exit}' "$SPEC_DIR"/result/lock.CPU2017)
  CORE_EXP_RESULT_DIR="$RESULT_DIR"/core_run/
  if [ ! -d "$CORE_EXP_RESULT_DIR" ];then
    echo
    mkdir "$CORE_EXP_RESULT_DIR"
  fi

  # Second experiment results
  for ((i=${FIRST_EXP_NUM}+2;i<=SECOND_EXP_NUM;i+=2))
  do
    cp "$SPEC_DIR"/result/CPU2017.$i.intspeed.refspeed.csv "$CORE_EXP_RESULT_DIR"
  done

  # Third experiment
  #echo $PW | sudo -S -E bash -c "$cmd3"

  # SPEC auto increment number after some scatter affinity experiments
  THIRD_EXP_NUM=$(awk '{print $1; exit}' "$SPEC_DIR"/result/lock.CPU2017)
  THREAD_EXP_RESULT_DIR="$RESULT_DIR"/thread_run/
  if [ ! -d "$THREAD_EXP_RESULT_DIR" ];then
    echo
    mkdir "$THREAD_EXP_RESULT_DIR"
  fi

  # Third experiment results
  for ((i=${SECOND_EXP_NUM}+2;i<=THIRD_EXP_NUM;i+=2))
  do
    cp "$SPEC_DIR"/result/CPU2017.$i.intspeed.refspeed.csv "$THREAD_EXP_RESULT_DIR"
  done

  # Revert changes to LLVM Target
  cd "$AARCH64_TARGET" || exit
  git apply -R "${SPEC_SCRIPT_DIR}"/config/aarch64.patch

  cd "$SPEC_SCRIPT_DIR" || exit

echo "==============================================="
done
git checkout development -- config/clang_modified.cfg config/info.json config/aarch64.patch
