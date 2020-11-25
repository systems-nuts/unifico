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

  export PATH=~/base_llvm/toolchain/bin/:$PATH
  export LD_LIBRARY_PATH=$(llvm-config --libdir)
  export NPB_RESULT_DIR=${NPB_SCRIPT_DIR}/results/${short_hash}

  git checkout "$short_hash" -- npb/config/make.def npb/config/suite.def npb/config/info.json

  cp "${NPB_SCRIPT_DIR}"/config/make.def "${NPB_DIR}"/config
  cp "${NPB_SCRIPT_DIR}"/config/suite.def "${NPB_DIR}"/config
  if [ ! -d "$NPB_RESULT_DIR" ];then
    echo
    mkdir "$NPB_RESULT_DIR"
  fi

  cp "${NPB_SCRIPT_DIR}"/config/info.json "${NPB_RESULT_DIR}"

  echo $PW | sudo -S -E bash -c "$cmd1"
  echo $PW | sudo -S -E bash -c "$cmd2"

  echo "==============================================="
done
git checkout development -- npb/config/make.def npb/config/suite.def npb/config/info.json
