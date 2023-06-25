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

import pandas as pd


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
                - ${npb_class}: The NPB class.
                - ${build_dir}: The name of the build directory of each NPB benchmark.
                - ${dest_dir}: Where to place the generated binaries after building.

                These are applied to the following config parameters:
                - "args"
                - "output"
                """
            ),
        )
        self.cmd_line_arguments(arg_parser)
        self.args = arg_parser.parse_args(args=args)

        # If a build was requested, the location of the NPB top-level folder should be provided
        if self.args.build:
            if not os.environ.get("NPB_PATH"):
                sys.exit(
                    "Error: Please set the location of top-level NPB folder path (NPB_PATH)"
                )

        self.cfg = json.loads("{}")
        with open(self.args.config) as jsonfile:
            self.cfg = json.load(jsonfile)

        if not len(self.cfg["executables"]):
            self.eprint("Error: No executables specified")
            exit(1)

        self.env = self.cfg["env"]
        for k in self.env:
            print(f"Setting env: {k} = {self.env[k]}")
            if not self.args.dryrun:
                os.environ[k] = self.env[k]

        self.cwd = os.getcwd()
        sep = "_"
        if self.args.dest:
            experiment_dir = self.args.dest
        else:
            now = datetime.now()
            date = now.strftime("%Y%m%d")
            time = now.strftime("%H%M%S")
            experiment_dir = os.path.join(self.cwd, sep.join([date, time]))

        if os.path.exists(experiment_dir):
            print(f'WARNING: "{experiment_dir}" already exists')

        if not self.args.dryrun and not os.path.exists(experiment_dir):
            print(f"Creating dir: {experiment_dir}")
            os.mkdir(experiment_dir)

        print(f"Changing working dir: {experiment_dir}")
        if not self.args.dryrun:
            os.chdir(experiment_dir)

        self.cwd = os.getcwd()
        self.bin_dir = self.get_abs_dir(self.cwd, self.cfg["bin_dir"])

    @staticmethod
    def cmd_line_arguments(arg_parser: argparse.ArgumentParser):
        """
        Registers all the command line arguments that are used by this tool.

        Add other/additional arguments by overloading this function.
        """
        arg_parser.add_argument(
            "-b", "--build", required=False, default=False, action="store_true"
        )
        arg_parser.add_argument(
            "-r", "--run", required=False, default=False, action="store_true"
        )
        arg_parser.add_argument(
            "-p",
            "--post-process",
            required=False,
            default=False,
            action="store_true",
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
        arg_parser.add_argument(
            "-d",
            "--dest",
            const=str,
            nargs="?",
            help="Optional destination directory name (default: timestamp)",
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

        print(f'Executing command: {" ".join(sargs)}')
        if not dryrun:
            subprocess.run(
                " ".join(sargs), shell=True, stderr=STDOUT, stdout=output
            )

    def build_benchmark(self, config, executable, dryrun=False):

        commands = config["build"]
        npb_class = config["npb_class"]

        for c in commands:
            # Assumes build dir are named bt/, cg/, etc, so you can infer the build dir from the first two letters.
            build_dir = executable[:2]
            if c["before"]:
                self.execute_cmd(
                    c["args"],
                    dryrun,
                    npb_class=npb_class,
                    build_dir=build_dir,
                    executable=executable,
                    output=c.get("output", ""),
                )

        for c in commands:
            # Assumes build dir are named bt/, cg/, etc, so you can infer the build dir from the first two letters.
            build_dir = executable[:2]
            if not c["before"]:
                self.execute_cmd(
                    c["args"],
                    dryrun,
                    build_dir=build_dir,
                    executable=executable,
                    dest_dir=self.bin_dir,
                    output="",
                )

    def build(self):
        print(f"Creating dir: {self.bin_dir}")
        if not self.args.dryrun and not os.path.exists(self.bin_dir):
            os.mkdir(self.bin_dir)

        build_dir = os.getenv("NPB_PATH")

        if not os.path.exists(build_dir):
            self.eprint(f'Error: "{build_dir}" does not exist!')
            exit(2)

        print(f"Changing working dir: {build_dir}")
        if not self.args.dryrun:
            os.chdir(build_dir)

        for benchmark in self.cfg["executables"]:
            bench_cfg = self.cfg["*"].copy()
            if benchmark in self.cfg:
                bench_cfg.update(self.cfg[benchmark])

            self.build_benchmark(bench_cfg, benchmark, self.args.dryrun)

    def execute_benchmark(self, config, executable, dryrun=False):

        commands = config["run"]

        for c in commands:
            if c["before"]:
                self.execute_cmd(
                    c["args"],
                    dryrun,
                    executable=executable,
                    output=c["output"],
                )

        # Main benchmark execution command
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

        run_wd = os.path.join(self.cwd, "run")
        if os.path.exists(run_wd):
            self.eprint(f'Error: "{run_wd}" already exists!')
            exit(2)

        print(f"Creating dir: {run_wd}")
        if not self.args.dryrun:
            os.mkdir(run_wd)

        print(f"Changing working dir: {run_wd}")
        if not self.args.dryrun:
            os.chdir(run_wd)

        for benchmark in self.cfg["executables"]:
            bench_cfg = self.cfg["*"].copy()
            if benchmark in self.cfg:
                bench_cfg.update(self.cfg[benchmark])

            if not int(bench_cfg["iterations"]):
                self.eprint(
                    f'Warning: "No iterations specified for {benchmark}!'
                )

            self.execute_benchmark(bench_cfg, benchmark, self.args.dryrun)

    def post_process_benchmark(self, config, executable, dryrun=False):

        commands = config["post_process"]

        for c in commands:
            # Assumes you can infer the benchmark name from the first two letters of the exe.
            benchmark = executable[:2]
            self.execute_cmd(
                c["args"],
                dryrun,
                benchmark=benchmark,
                executable=executable,
                output=c.get("output", ""),
            )

    def post_process(self):
        """
        Post-process the results produced by an experiment.

        The results are usually logs found in the `<experiment-name>/run` folder.
        Produces a .csv with aggregated and post-processed results.
        @return:
        """
        run_wd = os.path.join(self.cwd, "run")
        if not os.path.exists(run_wd):
            self.eprint(f'Error: "{run_wd}" does not exist!')
            exit(2)

        print(f"Changing working dir: {run_wd}")
        if not self.args.dryrun:
            os.chdir(run_wd)

        df = pd.DataFrame(columns=["benchmark", "time_O0"])
        df.to_csv("results.csv", index=False)

        for benchmark in self.cfg["executables"]:
            bench_cfg = self.cfg["*"].copy()
            if benchmark in self.cfg:
                bench_cfg.update(self.cfg[benchmark])

            self.post_process_benchmark(bench_cfg, benchmark, self.args.dryrun)

        df = pd.read_csv("results.csv")

    def dispatch(self):
        if self.args.build:
            self.build()
        if self.args.run:
            self.run()
        if self.args.post_process:
            self.post_process()


def __main__():
    npb_runner = NPBRunner()
    npb_runner.dispatch()


if __name__ == "__main__":
    __main__()
