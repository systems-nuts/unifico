#!/bin/bash

readelf --sections --wide call_leaf_x86-64_aligned.out >x86-64_sections.txt
readelf --sections --wide call_leaf_aarch64_aligned.out >aarch64_sections.txt
readelf --sections --wide call_leaf_x86-64_unaligned.out >un_x86-64_sections.txt
readelf --sections --wide call_leaf_aarch64_unaligned.out >un_aarch64_sections.txt
nm call_leaf_x86-64_aligned.out >nm_x86-64.txt
nm call_leaf_aarch64_aligned.out >nm_aarch64.txt
grep nm_aarch64.txt -e main
grep nm_x86-64.txt -e main
