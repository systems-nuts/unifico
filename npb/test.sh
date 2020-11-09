#!/bin/bash

cmd1="python3.7 -m npb.run_npb --suite-list suite.def --full-core-run --iterations=1"
cmd2="python3.7 -m npb.run_npb --suite-list suite.def --full-thread-run --iterations=1"

if [ $1 = "preview" ]; then
	cmd1+=" --preview"
	cmd2+=" --preview"
	shift
fi

echo "Testing.." 
echo "Result Directory: ${NPB_SCRIPT_DIR}/results/test"

export PATH=~/toolchain1/bin/:$PATH
export LD_LIBRARY_PATH=$(llvm-config --libdir)
export NPB_RESULT_DIR=${NPB_SCRIPT_DIR}/results/test

cp "${NPB_SCRIPT_DIR}"/config/make.def "${NPB_DIR}"/config
cp "${NPB_SCRIPT_DIR}"/config/test_suite.def "${NPB_DIR}"/config/suite.def
if [ ! -d "$NPB_RESULT_DIR" ]; then
echo
mkdir "$NPB_RESULT_DIR"
fi
rm -f "$NPB_RESULT_DIR"/*

bash -c "$cmd1"
bash -c "$cmd2"

for filename in "$NPB_RESULT_DIR"/*; do
	[ -e "$filename" ] || exit
	if grep -q "UNSUCCESSFUL" "$filename"; then
		echo "Not Verified!!!"
		exit
	fi
done
echo "Verified!!!"
