#!/usr/bin/env python3

import sys

from align.compare import compare_callsite_align

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: ", sys.argv[0], " <objdump_aarch64> <objdump_x86-64>")
        sys.exit(1)

    compare_callsite_align(sys.argv[1], sys.argv[2])
