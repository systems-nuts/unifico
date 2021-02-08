#!/bin/bash

LLVM_SOURCE=~/llvm-project
PATCH=~/phd/unified_abi/llvm_patches/llvm-9.patch
PATCHED_FILES=~/phd/unified_abi/layout/test_align/llvm_popcorn.txt

cd $LLVM_SOURCE || exit 1
git checkout -- .
git clean -d -f

while read p; do
  echo "$p"
  git apply --include=$p $PATCH 
done <$PATCHED_FILES
