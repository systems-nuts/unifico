#!/bin/bash

for file in is_aarch64.objdump is_aarch64_init.objdump; do
  get_files.sh nettuno phd/unified_abi/layout/npb3.3-ser-c-flat/is/build_aarch64/ $file
done

for file in is_x86_64.objdump is_x86_64_init.objdump; do
  get_files.sh nettuno phd/unified_abi/layout/npb3.3-ser-c-flat/is/build_x86-64/ $file
done

get_files.sh nettuno phd/unified_abi/layout/npb3.3-ser-c-flat/is/ is_cs_align.json
