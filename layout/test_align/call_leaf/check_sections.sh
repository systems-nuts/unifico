#!/bin/bash

readelf --sections --wide is_x86-64 >x86-64_sections.txt
readelf --sections --wide is_aarch64 >aarch64_sections.txt
nm is_aarch64 >nm_aarch64.txt
nm is_x86-64 >nm_x86-64.txt
grep nm_aarch64.txt -e main
grep nm_x86-64.txt -e main
grep nm_aarch64.txt -e add_7
grep nm_x86-64.txt -e add_7
