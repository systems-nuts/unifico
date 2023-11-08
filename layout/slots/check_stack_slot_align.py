#!/usr/bin/env python3

import argparse
import pathlib

from align.compare import compare_stack_slot_align

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""Compare callsite alignment.
        Current supported archs: [aarch64, x86_64]."""
    )
    parser.add_argument(
        "slot_debug1",
        type=pathlib.Path,
        help="A stack slot coloring debug file.",
    )
    parser.add_argument(
        "slot_debug2",
        type=pathlib.Path,
        help="A stack slot coloring debug file.",
    )
    args = parser.parse_args()

    compare_stack_slot_align(args.slot_debug1, args.slot_debug2)
