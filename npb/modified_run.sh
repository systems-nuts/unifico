#!/bin/bash

############################################
#
# Must have NPB_DIR and NPB_SCRIPT_DIR set.
#
############################################

WORKING_BRANCH=master

E_XCD=86 # Can't change directory?

CMD1="python3.7 -m npb.run_npb --suite-list suite.def --threads=1,2,4,6,8 --iterations=3"
CMD2="python3.7 -m npb.run_npb --suite-list suite.def --threads=1,2,4,6,8,10,12,14,16 --iterations=3"

if [ "$1" = "preview" ]; then
	CMD1+=" --preview"
	CMD2+=" --preview"
	shift
fi

# LLVM paths
PATH=~/my_llvm/toolchain/bin/:$PATH
LLVM_TARGET=~/llvm-project/llvm/lib/Target
BUILD_PATH=~/my_llvm/build
LD_LIBRARY_PATH=$(llvm-config --libdir)

# NPB Benchmark paths
NPB_CONF_DIR="$NPB_DIR"/config

# NPB development script paths
MAKE_CONF="$NPB_SCRIPT_DIR"/config/make.def
SUITE_CONF="$NPB_SCRIPT_DIR"/config/suite.def
EXPERIMENT_INFO="$NPB_SCRIPT_DIR"/config/info.json
LLVM_PATCH="$NPB_SCRIPT_DIR"/config/llvm.patch

echo "Give pass:"
read -s PW

for short_hash in "$@"
do
  echo "==============================================="

  git checkout "$short_hash" -- "$MAKE_CONF" "$SUITE_CONF" "$EXPERIMENT_INFO" "$LLVM_PATCH"

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
  ./build_exp.sh >/dev/null
  cmake --build . >/dev/null
  ninja install >/dev/null
  echo "Done"

  # Copy development config files to actual NPB Directory
  cp "$MAKE_CONF" "$NPB_CONF_DIR"
  cp "$SUITE_CONF" "$NPB_CONF_DIR"

  # Create results directory for the specific experiment commit hash.
  # Export it for the child processes to find
  export RESULT_DIR="$NPB_SCRIPT_DIR"/results/$short_hash
  if [ ! -d "$RESULT_DIR" ];then
    echo
    mkdir "$RESULT_DIR"
  fi
	
  # Return to working directory with NPB scripts
  cd "$NPB_SCRIPT_DIR" || {
    echo "Cannot change to necessary directory." # >&2 TODO
    exit $E_XCD;
  }
  cd .. || exit

  cp "$EXPERIMENT_INFO" "$RESULT_DIR"

  echo "Running experiments..."
  echo "$PW" | sudo -S -E PATH="$PATH" LD_LIBRARY_PATH="$LD_LIBRARY_PATH" bash -c "$CMD1"
  #echo $PW | sudo -S -E PATH=$PATH LD_LIBRARY_PATH=$LD_LIBRARY_PATH bash -c "$CMD2"
  echo "Done"

  # Revert changes to LLVM Target
  cd "$LLVM_TARGET" || {
    echo "Cannot change to necessary directory." # >&2 TODO
    exit $E_XCD;
  }
  git apply -R "$LLVM_PATCH"

  # Go to result dir and verify results
  cd "$NPB_SCRIPT_DIR" || {
    echo "Cannot change to necessary directory." # >&2 TODO
    exit $E_XCD;
  }
  echo "Verifying..."
  for filename in "$RESULT_DIR"/*; do
	  [ -f "$filename" ] || continue
	  if grep -q "UNSUCCESSFUL" "$filename"; then
	  	echo "Not Verified!!!"
	  	exit
	  fi
  done
  echo "Success!"

echo "+++++++++++++++++++++++++++++++++++++++++++++++"
done

# Get back previous config files
git checkout $WORKING_BRANCH -- "$MAKE_CONF" "$SUITE_CONF" "$EXPERIMENT_INFO" "$LLVM_PATCH"
