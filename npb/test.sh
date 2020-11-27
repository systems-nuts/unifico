#!/bin/bash

cmd1="python3.7 -m npb.run_npb --suite-list suite.def --threads=1,2,4,6,8 --iterations=1"
cmd2="python3.7 -m npb.run_npb --suite-list suite.def --threads=1,2,4,6,8,10,12,14,16 --iterations=1"

if [ $1 = "preview" ]; then
	cmd1+=" --preview"
	cmd2+=" --preview"
	shift
fi

echo "Testing..."

echo "Give pass:"
read -s PW

export PATH=~/base_llvm/toolchain/bin/:$PATH
export LD_LIBRARY_PATH=$(llvm-config --libdir)
export NPB_RESULT_DIR=${NPB_SCRIPT_DIR}/results/test

cp "${NPB_SCRIPT_DIR}"/config/make.def "${NPB_DIR}"/config
cp "${NPB_SCRIPT_DIR}"/config/test_suite.def "${NPB_DIR}"/config/suite.def

if [ ! -d "$NPB_RESULT_DIR" ]; then
echo
mkdir "$NPB_RESULT_DIR"
fi
rm -f "$NPB_RESULT_DIR"/*

echo $PW | sudo -S -E PATH=$PATH LD_LIBRARY_PATH=$LD_LIBRARY_PATH bash -c "$cmd1"
echo $PW | sudo -S -E PATH=$PATH LD_LIBRARY_PATH=$LD_LIBRARY_PATH bash -c "$cmd2"

for filename in "$NPB_RESULT_DIR"/*; do
	[ -e "$filename" ] || exit
	if grep -q "UNSUCCESSFUL" "$filename"; then
		echo "Not Verified!!!"
		exit
	fi
done
echo "Verified!!!"
