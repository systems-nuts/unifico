#!/usr/bin/env python3

# TODO consider eliding prepend/append from config
# TODO extend string templating
# TODO consider JSON schema for config file

import os
import sys
import argparse
import json
import textwrap

import subprocess
from subprocess import STDOUT, DEVNULL

from datetime import datetime
from string import Template


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_abs_dir(cwd, bindir):
    return bindir if os.path.isabs(bindir) else os.path.join(cwd, bindir)


def execute_cmd(args, dryrun=False, **kwargs):
    output = DEVNULL

    f = Template(kwargs["output"]).safe_substitute(**kwargs).strip()
    kwargs["output"] = f
    if f != "" and not dryrun:
        output = open(f, "wb")

    sargs = [Template(arg).safe_substitute(**kwargs) for arg in args]

    print(f'executing command: {" ".join(sargs)}')
    if not dryrun:
        subprocess.run(
            " ".join(sargs), shell=True, stderr=STDOUT, stdout=output
        )


def execute_bmks(config, executable, dryrun=False):
    env = config["env"]

    for k in env:
        print(f"setting env: {k} = {env[k]}")
        if not dryrun:
            os.environ[k] = env[k]

    commands = config["commands"]

    for c in commands:
        if c["before"]:
            execute_cmd(
                c["args"], dryrun, executable=executable, output=c["output"]
            )

    cmd = os.path.join(f"{config['bindir']}", f"{executable}")

    for i in range(config["iterations"]):
        execute_cmd(
            [*config["prepend"], cmd, *config["append"]],
            dryrun,
            executable=executable,
            iteration=i,
            output=config["output"],
        )

    for c in commands:
        if not c["before"]:
            execute_cmd(
                c["args"], dryrun, executable=executable, output=c["output"]
            )


#

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Run benchmarks.",
        epilog=textwrap.dedent(
            """
            The following $-based substitutions are supported:
            - ${executable}: The current executable being used from the
            \"executables\" config parameter.
            - ${iteration}: The current iteration being performed based on the
            "iterations" config parameter.

            These are applied to the following config parameters:
            - "args"
            - "output"
            """
        ),
    )
    parser.add_argument(
        "-c",
        "--config",
        const=str,
        nargs="?",
        help="Configuration file for running benchmarks",
    )
    parser.add_argument(
        "-n",
        "--dryrun",
        action="store_true",
        help="Perform only dry run",
    )
    args = parser.parse_args()

    cfg = json.loads("{}")
    with open(args.config) as jsonfile:
        cfg = json.load(jsonfile)

    if not len(cfg["executables"]):
        eprint("error: no executables to run specified")
        exit(1)

    cwd = os.getcwd()
    now = datetime.now()
    date = now.strftime("%Y%m%d")
    time = now.strftime("%H%M%S")
    sep = "_"
    run_wd = os.path.join(cwd, sep.join(["run", *cfg["tags"], date, time]))

    if os.path.exists(run_wd):
        eprint('error: "{run_wd}" already exists!')
        exit(2)

    print(f"creating dir: {run_wd}")
    if not args.dryrun:
        os.mkdir(run_wd)

    print(f"changing working dir: {run_wd}")
    if not args.dryrun:
        os.chdir(run_wd)

    for e in cfg["executables"]:
        ecfg = cfg["*"].copy()
        if e in cfg:
            ecfg.update(cfg[e])

        if not int(ecfg["iterations"]):
            eprint('warning: "no iterations specified for {e}!')

        ecfg["bindir"] = get_abs_dir(cwd, ecfg["bindir"])

        execute_bmks(ecfg, e, args.dryrun)
