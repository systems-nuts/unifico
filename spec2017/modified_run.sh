#!/bin/bash

WORKING_BRANCH=refactor_spec_run

E_XCD=86 # Can't change directory?

CMD1="python3.7 -m spec2017.run_spec --config-list clang_modified.cfg --threads=1 \
      --bench=600,602,605,625 --iterations=3 --noreportable --tune=base -i test,train,refspeed"
CMD2="python3.7 -m spec2017.run_spec --config-list clang_modified.cfg \
      --threads=1,2,4,6,8 --bench 657 --iterations=3 --noreportable --tune=base -i test,train,refspeed"
CMD3="python3.7 -m spec2017.run_spec --config-list clang_modified.cfg --full-thread-run \
      --bench 657 --iterations=3 --noreportable --tune=base -i test,train,refspeed"

if [ "$1" = "preview" ]; then
	CMD1+=" --preview"
	CMD2+=" --preview"
	CMD3+=" --preview"
	shift
fi

# LLVM paths
PATH=~/my_llvm/toolchain/bin/:$PATH
LLVM_TARGET=~/llvm-project/llvm/lib/Target
BUILD_PATH=~/my_llvm/build
LD_LIBRARY_PATH=$(llvm-config --libdir)

# SPEC2017 Benchmark paths
SPEC_DIR=/home/nikos/cpu2017
SPEC_CONF_DIR="$SPEC_DIR"/config
SPEC_RESULT_DIR="$SPEC_DIR"/result

# SPEC2017 development script paths
CONFIG_FILE="$SPEC_SCRIPT_DIR"/config/clang_modified.cfg
EXPERIMENT_INFO="$SPEC_SCRIPT_DIR"/config/info.json
LLVM_PATCH="$SPEC_SCRIPT_DIR"/config/llvm.patch

echo "Give pass:"
read -r -s PW
	
for short_hash in "$@"
do
  echo "==============================================="

  git checkout "$short_hash" -- "$CONFIG_FILE" "$EXPERIMENT_INFO" "$LLVM_PATCH"

  # Apply changes to LLVM Target
  cd "$LLVM_TARGET" || {
    echo "Cannot change to necessary directory." # >&2 TODO
    exit $E_XCD;
  }
  git apply -- "$LLVM_PATCH"

  # Build LLVM Target
  cd "$BUILD_PATH" || {
    echo "Cannot change to necessary directory." # >&2 TODO
    exit $E_XCD;
  }
  echo "Building..."
  ./build_exp.sh
  cmake --build .
  ninja install
  echo "Done"

  cd "$SPEC_SCRIPT_DIR" || exit
  cd .. || exit

  cp "$CONFIG_FILE" "$SPEC_CONF_DIR"

  # First Experiment
  echo "$PW" | sudo -S -E bash -c "$CMD1"

  # SPEC auto increment number after one serial experiments
  FIRST_EXP_NUM=$(awk '{print $1; exit}' "$SPEC_RESULT_DIR"/lock.CPU2017)

  # Create results directory for the specific experiment commit hash using auto-increment lock.
  # Export it for the child processes to find
  export RESULT_DIR="$SPEC_SCRIPT_DIR"/results/${FIRST_EXP_NUM}_${short_hash}
  if [ ! -d "$RESULT_DIR" ];then
    echo
    mkdir "$RESULT_DIR"
  fi

  SERIAL_EXP_RESULT_DIR="$RESULT_DIR"/serial
  CORE_EXP_RESULT_DIR="$RESULT_DIR"/core
  THREAD_EXP_RESULT_DIR="$RESULT_DIR"/thread

  # General info on the experiment
  cp "$EXPERIMENT_INFO" "$RESULT_DIR"

  # Serial experiment directory
  if [ ! -d "$SERIAL_EXP_RESULT_DIR" ];then
    echo
    mkdir "$SERIAL_EXP_RESULT_DIR"
  fi

  # First Experiment Results
  cp "$SPEC_RESULT_DIR"/CPU2017."$FIRST_EXP_NUM".intspeed.refspeed.csv "$SERIAL_EXP_RESULT_DIR"

  # Second Experiment
  echo "$PW" | sudo -S -E bash -c "$CMD2"

  # SPEC auto increment number after some compact affinity experiments
  SECOND_EXP_NUM=$(awk '{print $1; exit}' "$SPEC_DIR"/result/lock.CPU2017)
  if [ ! -d "$CORE_EXP_RESULT_DIR" ];then
    echo
    mkdir "$CORE_EXP_RESULT_DIR"
  fi

  # Second experiment results
  for ((i=FIRST_EXP_NUM+2;i<=SECOND_EXP_NUM;i+=2))
  do
    cp "$SPEC_DIR"/result/CPU2017.$i.intspeed.refspeed.csv "$CORE_EXP_RESULT_DIR"
  done

  # Third experiment
  # echo "$PW" | sudo -S -E bash -c "$CMD3"

  # SPEC auto increment number after some scatter affinity experiments
  THIRD_EXP_NUM=$(awk '{print $1; exit}' "$SPEC_DIR"/result/lock.CPU2017)
  if [ ! -d "$THREAD_EXP_RESULT_DIR" ];then
    echo
    mkdir "$THREAD_EXP_RESULT_DIR"
  fi

  # Third experiment results
  for ((i=SECOND_EXP_NUM+2;i<=THIRD_EXP_NUM;i+=2))
  do
    cp "$SPEC_DIR"/result/CPU2017.$i.intspeed.refspeed.csv "$THREAD_EXP_RESULT_DIR"
  done

  # Revert changes to LLVM Target
  cd "$LLVM_TARGET" || {
    echo "Cannot change to necessary directory." # >&2 TODO
    exit $E_XCD;
  }
  git apply -R "$LLVM_PATCH"

  cd "$SPEC_SCRIPT_DIR" || {
    echo "Cannot change to necessary directory." # >&2 TODO
    exit $E_XCD;
  }
echo "+++++++++++++++++++++++++++++++++++++++++++++++"
done

# Get back previous config files
git checkout $WORKING_BRANCH -- "$CONFIG_FILE" "$EXPERIMENT_INFO" "$LLVM_PATCH"
