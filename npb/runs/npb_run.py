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


class NPBRunner:
    def __init__(self, args=None):
        arg_parser = argparse.ArgumentParser(
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
        self.cmd_line_arguments(arg_parser)
        self.args = arg_parser.parse_args(args=args)

        self.cfg = json.loads("{}")
        with open(self.args.config) as jsonfile:
            self.cfg = json.load(jsonfile)

        self.cwd = os.getcwd()
        self.bin_dir = self.get_abs_dir(self.cwd, self.cfg["bin_dir"])

    @staticmethod
    def cmd_line_arguments(arg_parser: argparse.ArgumentParser):
        """
        Registers all the command line arguments that are used by this tool.

        Add other/additional arguments by overloading this function.
        """
        arg_parser.add_argument(
            "-r", "--run", required=False, default=False, action="store_true"
        )
        arg_parser.add_argument(
            "-c",
            "--config",
            const=str,
            nargs="?",
            help="Configuration file for running benchmarks",
        )
        arg_parser.add_argument(
            "-n",
            "--dryrun",
            action="store_true",
            help="Perform only dry run",
        )

    @staticmethod
    def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)

    @staticmethod
    def get_abs_dir(cwd, bindir):
        return bindir if os.path.isabs(bindir) else os.path.join(cwd, bindir)

    @staticmethod
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

    def execute_benchmark(self, config, executable, dryrun=False):
        env = config["env"]

        for k in env:
            print(f"setting env: {k} = {env[k]}")
            if not dryrun:
                os.environ[k] = env[k]

        commands = config["commands"]

        for c in commands:
            if c["before"]:
                self.execute_cmd(
                    c["args"],
                    dryrun,
                    executable=executable,
                    output=c["output"],
                )

        cmd = os.path.join(f"{self.bin_dir}", f"{executable}")

        for i in range(config["iterations"]):
            self.execute_cmd(
                [*config["prepend"], cmd, *config["append"]],
                dryrun,
                executable=executable,
                iteration=i,
                output=config["output"],
            )

        for c in commands:
            if not c["before"]:
                self.execute_cmd(
                    c["args"],
                    dryrun,
                    executable=executable,
                    output=c["output"],
                )

    def run(self):
        if not len(self.cfg["executables"]):
            self.eprint("error: no executables to run specified")
            exit(1)

        now = datetime.now()
        date = now.strftime("%Y%m%d")
        time = now.strftime("%H%M%S")
        sep = "_"
        run_wd = os.path.join(
            self.cwd, sep.join(["run", *self.cfg["tags"], date, time])
        )

        if os.path.exists(run_wd):
            self.eprint('error: "{run_wd}" already exists!')
            exit(2)

        print(f"creating dir: {run_wd}")
        if not self.args.dryrun:
            os.mkdir(run_wd)

        print(f"changing working dir: {run_wd}")
        if not self.args.dryrun:
            os.chdir(run_wd)

        for benchmark in self.cfg["executables"]:
            bench_cfg = self.cfg["*"].copy()
            if benchmark in self.cfg:
                bench_cfg.update(self.cfg[benchmark])

            if not int(bench_cfg["iterations"]):
                self.eprint(
                    'warning: "no iterations specified for {benchmark}!'
                )

            self.execute_benchmark(bench_cfg, benchmark, self.args.dryrun)

    def dispatch(self):
        if self.args.run:
            self.run()


def __main__():
    npb_runner = NPBRunner()
    npb_runner.dispatch()


if __name__ == "__main__":
    __main__()
