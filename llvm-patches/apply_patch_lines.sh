#!/bin/bash

LLVM_SOURCE=~/llvm-project
PATCH_FOLDER=~/phd/unified_abi/llvm_patches/llvm-9.0.1

cd $LLVM_SOURCE || exit 1
git clean -d -f
git checkout -- .

for filename in ${PATCH_FOLDER}/*.patch; do
	echo "Applying ${filename}..."
  	git apply ${filename} || exit 1
done 

echo 'Done!'
