#!/bin/bash

cmd1="python3.7 -m npb.run_npb --suite-list suite.def --threads=1,2,4,6,8 --iterations=3"
cmd2="python3.7 -m npb.run_npb --suite-list suite.def --threads=1,2,4,6,8,10,12,14,16 --iterations=3"

if [ "$1" = "preview" ]; then
	cmd1+=" --preview"
	cmd2+=" --preview"
	shift
fi

echo "Give pass:"
read -s PW

for short_hash in "$@"
do
  echo "==============================================="

  export PATH=~/my_llvm/toolchain/bin/:$PATH
  export LLVM_TARGET=~/llvm-project/llvm/lib/Target
  export BUILD_PATH=~/my_llvm/build
  export LD_LIBRARY_PATH=$(llvm-config --libdir)
  export NPB_RESULT_DIR=${NPB_SCRIPT_DIR}/results/${short_hash}

  git checkout "$short_hash" -- npb/config/make.def npb/config/suite.def npb/config/info.json npb/config/llvm.patch

  # Apply changes to LLVM Target
  cd "$LLVM_TARGET" || exit
  git apply -- "${NPB_SCRIPT_DIR}"/config/llvm.patch
  cd "$BUILD_PATH" || exit
  ./build_exp.sh
  cmake --build .
  ninja install

  cd "$NPB_SCRIPT_DIR" || exit
  cd .. || exit

  cp "${NPB_SCRIPT_DIR}"/config/make.def "${NPB_DIR}"/config
  cp "${NPB_SCRIPT_DIR}"/config/suite.def "${NPB_DIR}"/config
  if [ ! -d "$NPB_RESULT_DIR" ];then
    echo
    mkdir "$NPB_RESULT_DIR"
  fi

  cp "${NPB_SCRIPT_DIR}"/config/info.json "${NPB_RESULT_DIR}"

  echo $PW | sudo -S -E bash -c "$cmd1"
  echo $PW | sudo -S -E bash -c "$cmd2"

  # Revert changes to LLVM Target
  cd "$LLVM_TARGET" || exit
  git apply -R "${NPB_SCRIPT_DIR}"/config/llvm.patch

  cd "$NPB_SCRIPT_DIR" || exit

echo "==============================================="
done
git checkout development -- config/make.def config/suite.def config/info.json
