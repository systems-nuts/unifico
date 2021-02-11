#!/bin/bash

LLVM_SOURCE=~/llvm-project
POPCORN_PATCH=~/unified_abi/llvm_patches/llvm-9.patch
POPCORN_PATCHED_FILES=~/unified_abi/llvm_patches/llvm_popcorn.txt
ALIGN_PATCH=~/unified_abi/llvm_patches/align.patch

cd $LLVM_SOURCE || exit 1
git checkout -- .
git clean -d -f

echo 'Applying popcorn patch...'
while read p; do
  echo "$p"
  git apply --include=$p $ALIGN_PATCH 
done <$POPCORN_PATCHED_FILES

echo 'Done!'
