#!/bin/bash

##### FIXME #####
# Git branch
WORKING_BRANCH=marcus-test

# LLVM paths
LLVM_SOURCE=~/llvm-project
BUILD_PATH=~/llvm-9/build
#################

E_XCD=86 # Can't change directory?

commit_hash=$1

cd "$LLVM_SOURCE" || {
	echo "Cannot change to llvm source tree." 
	exit $E_XCD;
}

git checkout $commit_hash

# Build LLVM Target
cd "$BUILD_PATH" || {
	echo "Cannot change to llvm build directory." 
	exit $E_XCD;
}

echo "Building..."
./build_exp.sh >/dev/null
cmake --build . >/dev/null
ninja install >/dev/null
echo "Done!"

# Return to llvm source tree and undo the changes
cd "$LLVM_SOURCE" || {
	echo "Cannot change to llvm source tree." 
	exit $E_XCD;
}

git checkout $WORKING_BRANCH

