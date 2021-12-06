#!/bin/bash

bench=is

for file in ${bench}_aarch64.objdump ${bench}_aarch64_init.objdump; do
  get_files.sh nettuno phd/unified_abi/layout/npb3.3-ser-c-flat/${bench}/build_aarch64/ $file
done

for file in ${bench}_x86_64.objdump ${bench}_x86_64_init.objdump; do
  get_files.sh nettuno phd/unified_abi/layout/npb3.3-ser-c-flat/${bench}/build_x86-64/ $file
done

get_files.sh nettuno phd/unified_abi/layout/npb3.3-ser-c-flat/${bench}/ ${bench}_cs_align.json
