#!/bin/bash

cmd1="python3.7 -m spec2017.run_spec --config-list spec2017/config/clang_modified.cfg --threads=1 \
      --bench=600,602,605,625 --iterations=1 --noreportable --tune=base -i test"
cmd2="python3.7 -m spec2017.run_spec --config-list spec2017/config/clang_modified.cfg --threads=2,4 \
      --compact-affinity --bench 657 --iterations=1 --noreportable --tune=base -i test"
cmd3="python3.7 -m spec2017.run_spec --config-list spec2017/config/clang_modified.cfg --threads=2,4 \
      --bench 657 --iterations=1 --noreportable --tune=base -i test"

if [ "$1" = "preview" ]; then
	cmd1+=" --preview"
	cmd2+=" --preview"
	cmd3+=" --preview"
	shift
fi
	
echo "==============================================="

export PATH=~/my_llvm/toolchain_exp/bin/:$PATH
export X86_TARGET=~/llvm-project/llvm/lib/Target/X86
export BUILD_PATH=~/my_llvm/build_exp
export LD_LIBRARY_PATH=$(llvm-config --libdir)
export SPEC_DIR=/home/nikos/cpu2017

# Apply changes to LLVM Target
cd "$X86_TARGET" || exit
git apply -- "${SPEC_SCRIPT_DIR}"/config/x86.patch
cd "$BUILD_PATH" || exit
./build_exp.sh
cmake --build .
ninja install

cd "$SPEC_SCRIPT_DIR" || exit
cd .. || exit

echo "Give pass:"
read -s PW

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
cp "$SPEC_DIR"/result/CPU2017."$FIRST_EXP_NUM".intspeed.test.csv "$RESULT_DIR"
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
for ((i=FIRST_EXP_NUM+2;i<=SECOND_EXP_NUM;i+=2))
do
cp "$SPEC_DIR"/result/CPU2017.$i.intspeed.test.csv "$CORE_EXP_RESULT_DIR"
done

# Third experiment
echo $PW | sudo -S -E bash -c "$cmd3"

# SPEC auto increment number after some scatter affinity experiments
THIRD_EXP_NUM=$(awk '{print $1; exit}' "$SPEC_DIR"/result/lock.CPU2017)
THREAD_EXP_RESULT_DIR="$RESULT_DIR"/thread_run/
if [ ! -d "$THREAD_EXP_RESULT_DIR" ];then
echo
mkdir "$THREAD_EXP_RESULT_DIR"
fi

# Third experiment results
for ((i=SECOND_EXP_NUM+2;i<=THIRD_EXP_NUM;i+=2))
do
cp "$SPEC_DIR"/result/CPU2017.$i.intspeed.test.csv "$THREAD_EXP_RESULT_DIR"
done

# Revert changes to LLVM Target
cd "$X86_TARGET" || exit
git apply -R "${SPEC_SCRIPT_DIR}"/config/x86.patch

cd "$SPEC_SCRIPT_DIR" || exit

echo "==============================================="
