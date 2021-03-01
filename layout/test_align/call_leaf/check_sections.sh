#!/bin/bash

readelf --sections --wide call_leaf_x86-64 >x86-64_sections.txt
readelf --sections --wide call_leaf_aarch64 >aarch64_sections.txt
nm call_leaf_x86-64 >nm_x86-64.txt
nm call_leaf_aarch64 >nm_aarch64.txt
grep nm_aarch64.txt -e main
grep nm_x86-64.txt -e main
grep nm_aarch64.txt -e add_7
grep nm_x86-64.txt -e add_7
