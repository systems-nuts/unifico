#!/usr/bin/env python3

import argparse
import pathlib

from align.compare import compare_callsite_align

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Compare callsite alignment.
        Current supported archs: [aarch64, x86_64]."""
    )
    parser.add_argument(
        "objdump1", type=pathlib.Path, help="An objdump input file."
    )
    parser.add_argument(
        "objdump2", type=pathlib.Path, help="An objdump input file."
    )
    args = parser.parse_args()

    compare_callsite_align(args.objdump1, args.objdump2)
