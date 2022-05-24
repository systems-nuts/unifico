#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import json

from datetime import datetime


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_abs_dir(cwd, bindir):
    return bindir if os.path.isabs(bindir) else os.path.join(cwd, bindir)


def shell_execute(c):
    subprocess.run(c, shell=True)


def execute_cmd(config, executable, dryrun=False):
    env = config["env"]

    for k in env:
        print(f"setting env: {k} = {env[k]}")
        if not dryrun:
            os.environ[k] = env[k]

    for c in config["precmd"]:
        print(f'executing pre command: "{c}"')
        if not dryrun:
            shell_execute(c)

    cmd = os.path.join(f"{config['bindir']}", f"{executable}")

    print(f'executing ({config["iterations"]} times) command: "{cmd}"')
    if not dryrun:
        for i in range(config["iterations"]):
            log_file = f"run_{executable}_{i}.log"
            rc = subprocess.run(
                [*config["prepend"], cmd, *config["append"]],
                stderr=subprocess.STDOUT,
                stdout=open(log_file, "wb"),
            )
            print(rc.args)

    for c in config["postcmd"]:
        print(f'executing post command: "{c}"')
        if not dryrun:
            shell_execute(c)


#

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run benchmarks.")
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

        execute_cmd(ecfg, e, args.dryrun)
