#!/bin/bash

readelf --sections --wide call_leaf_x86-64_aligned.out >x86-64_sections.txt
readelf --sections --wide call_leaf_aarch64_aligned.out >aarch64_sections.txt
readelf --sections --wide call_leaf_x86-64_unaligned.out >x86-64_sections.txt
readelf --sections --wide call_leaf_aarch64_unaligned.out >aarch64_sections.txt
