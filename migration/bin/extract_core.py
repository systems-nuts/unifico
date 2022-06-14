#!/usr/bin/env python3

import sys
import os
import argparse

import subprocess
from subprocess import STDOUT


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Run coredump extraction.",
    )
    parser.add_argument(
        "-c",
        "--config",
        nargs=1,
        required=True,
        help="Config file describing migration point.",
    )
    parser.add_argument(
        "-e",
        "--executable",
        nargs=1,
        required=True,
        help="Executable to use for extracting migration coredump.",
    )
    parser.add_argument(
        "-d",
        "--coredump",
        nargs=1,
        help="Coredump file to use from previous execution.",
    )
    parser.add_argument(
        "-n",
        "--dryrun",
        action="store_true",
        help="Perform only dry run",
    )
    args = parser.parse_args()

    lib = os.path.join(
        os.path.dirname(__file__), "../lib/util/gdb/", "migrate.py"
    )
    cmd = [
        "gdb",
        f"-x {os.path.abspath(lib)}",
        f'-ex "migrate {args.config[0]}"',
        '-ex "timed-run"',
        '-ex "quit"',
    ]

    if args.coredump:
        cmd.append(f"-c {args.coredump[0]}")

    cmd.append(args.executable[0])

    if args.dryrun:
        print(f'executing command: {" ".join(cmd)}')
    else:
        subprocess.run(" ".join(cmd), shell=True, stderr=STDOUT)
