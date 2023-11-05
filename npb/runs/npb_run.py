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
from scipy.stats import gmean

import pandas as pd

KNOWN_FAILURES = [("ft", "C"), ("mg", "C")]


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

        if self.args.compare:
            self.compare_dir = self.args.compare

        sep = "_"
        if self.args.dest:
            experiment_dir = self.args.dest
        else:
            now = datetime.now()
            date = now.strftime("%Y%m%d")
            time = now.strftime("%H%M%S")
            experiment_dir = sep.join([date, time])

        if os.path.exists(experiment_dir):
            print(f'WARNING: "{experiment_dir}" already exists')

        if not self.args.dryrun and not os.path.exists(experiment_dir):
            print(f"Creating dir: {experiment_dir}")
            os.makedirs(experiment_dir, exist_ok=True)

        print(f"Changing working dir: {experiment_dir}")
        if not self.args.dryrun:
            os.chdir(experiment_dir)

        self.experiment_dir = experiment_dir
        self.cwd = os.getcwd()
        self.bin_dir = self.get_abs_dir(
            self.cwd, self.cfg.get("bin_dir", "bin")
        )
        self.run_dir = self.get_abs_dir(
            self.cwd, self.cfg.get("run_dir", "run")
        )

        self.metric = self.args.metric
        self.npb_class = self.args.npb_class

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
        arg_parser.add_argument(
            "-m",
            "--compare",
            const=str,
            nargs="?",
            help="Optional base directory to compare results with. "
            "Prints a comparison csv on the destination directory",
        )
        arg_parser.add_argument(
            "--metric",
            const=str,
            nargs="?",
            default="time",
            help="Optional metric name to use when post-processing (default: time)",
        )
        arg_parser.add_argument(
            "--npb-class",
            const=int,
            nargs="?",
            default="S",
            help="NPB Class size to run (default: S)",
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
            result = subprocess.run(
                " ".join(sargs), shell=True, stderr=STDOUT, stdout=output
            )
            if f != "":
                output.close()
            if result.returncode != 0:
                print(f"Error: Command failed: {' '.join(sargs)}")
                if f != "":
                    print(f"Output file: ")
                    print("====== OUTPUT START ======")
                    with open(f, "r") as f:
                        print(f.read())
                    print("====== OUTPUT END ======")
                exit(1)

    @staticmethod
    def combine_dataframes_column(df1, df2, column=None):
        if not column:
            column = df1.columns[0]
            assert (
                column in df2.columns
            ), f"{column} missing in second dataframe"
        df_results = pd.DataFrame(index=df1.index)
        df_results["{}_overhead".format(column)] = df1[column].combine(
            df2[column], lambda x1, x2: (x2 / x1 - 1) * 100
        )
        df_results["{}_speedup".format(column)] = df1[column].combine(
            df2[column], lambda x1, x2: x1 / x2
        )
        return df_results

    def build_benchmark(self, config, executable, dryrun=False):
        commands = config["build"]

        # Assumes build dir are named bt/, cg/, etc, so you can infer the build dir from the first two letters.
        build_dir = executable[:2]
        if (build_dir, self.npb_class) in KNOWN_FAILURES:
            print(
                f'WARNING: "Skipping {build_dir}/{self.npb_class} combo because of known failures"'
            )
            return

        for c in commands:
            if c["before"]:
                self.execute_cmd(
                    c["args"],
                    dryrun,
                    npb_class=self.npb_class,
                    build_dir=build_dir,
                    executable=executable,
                    output=c.get("output", ""),
                )

        for c in commands:
            if not c["before"]:
                self.execute_cmd(
                    c["args"],
                    dryrun,
                    npb_class=self.npb_class,
                    build_dir=build_dir,
                    executable=executable,
                    dest_dir=self.bin_dir,
                    output=c.get("output", ""),
                )

    def build(self):
        if not self.args.dryrun and not os.path.exists(self.bin_dir):
            print(f"Creating dir: {self.bin_dir}")
            os.makedirs(self.bin_dir, exist_ok=True)

        suite_dir = os.getenv("NPB_PATH")

        if not os.path.exists(suite_dir):
            self.eprint(f'Error: "{suite_dir}" does not exist!')
            exit(2)

        print(f"Changing working dir: {suite_dir}")
        if not self.args.dryrun:
            os.chdir(suite_dir)

        for benchmark in self.cfg["executables"]:
            bench_cfg = self.cfg["*"].copy()
            if benchmark in self.cfg:
                bench_cfg.update(self.cfg[benchmark])

            self.build_benchmark(bench_cfg, benchmark, self.args.dryrun)

    def execute_benchmark(self, config, executable, dryrun=False):
        commands = config["run"]
        # Assumes you can infer the benchmark name from the first two letters of the exe.
        benchmark = executable[:2]
        if (benchmark, self.npb_class) in KNOWN_FAILURES:
            print(
                f'WARNING: "Skipping {benchmark}/{self.npb_class} combo because of known failures"'
            )
            return

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
                npb_class=self.npb_class,
                executable=executable,
                iteration=i,
                output=config["output"],
            )

        for c in commands:
            if not c["before"]:
                self.execute_cmd(
                    c["args"],
                    dryrun,
                    npb_class=self.npb_class,
                    executable=executable,
                    output=c["output"],
                )

    def run(self):
        if not self.args.dryrun and not os.path.exists(self.run_dir):
            print(f"Creating dir: {self.run_dir}")
            os.makedirs(self.run_dir, exist_ok=True)

        print(f"Changing working dir: {self.run_dir}")
        if not self.args.dryrun:
            os.chdir(self.run_dir)

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
        # Assumes you can infer the benchmark name from the first two letters of the exe.
        benchmark = executable[:2]
        if (benchmark, self.npb_class) in KNOWN_FAILURES:
            print(
                f'WARNING: "Skipping {benchmark}/{self.npb_class} combo because of known failures"'
            )
            return

        for c in commands:
            self.execute_cmd(
                c["args"],
                dryrun,
                npb_class=self.npb_class,
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
        if not os.path.exists(self.run_dir):
            self.eprint(f'Error: "{self.run_dir}" does not exist!')
            exit(2)

        print(f"Changing working dir: {self.run_dir}")
        if not self.args.dryrun:
            os.chdir(self.run_dir)

        results_csv = f"results_{self.npb_class}.csv"

        df = pd.DataFrame(columns=["benchmark", self.metric])
        df.to_csv(results_csv, index=False)

        for benchmark in self.cfg["executables"]:
            bench_cfg = self.cfg["*"].copy()
            if benchmark in self.cfg:
                bench_cfg.update(self.cfg[benchmark])

            self.post_process_benchmark(bench_cfg, benchmark, self.args.dryrun)

        df = pd.read_csv(results_csv, index_col="benchmark")
        df = df.apply(pd.to_numeric)
        df.loc["Geomean"] = df.apply(gmean, axis=0)
        df = df.round(2)
        df.to_csv(results_csv)

    def compare(self):
        """
        Compare the results of the destination directory with the ones in base directory.

        Assumes that there is a results.csv in both directories.
        Produces a .csv with the comparison results.
        @return:
        """
        results_csv = f"results_{self.npb_class}.csv"

        df_current = pd.read_csv(
            os.path.join(self.run_dir, results_csv), index_col="benchmark"
        )
        df_base = pd.read_csv(
            os.path.join(self.compare_dir, results_csv),
            index_col="benchmark",
        )
        df_overhead = self.combine_dataframes_column(df_base, df_current)
        df_overhead = df_overhead.drop("Geomean", axis=0)
        mean_metric = df_overhead.mean(axis=0)
        geomean_metric = df_overhead.apply(gmean, axis=0)
        df_overhead.loc["Mean"] = mean_metric
        df_overhead.loc["Geomean"] = geomean_metric
        df_overhead = df_overhead.round(2)

        overhead_csv = f"overhead_{self.npb_class}.csv"
        print(f"Dumping overhead results to {overhead_csv}")
        df_overhead.to_csv(overhead_csv, header=True)

    def dispatch(self):
        if self.args.build:
            self.build()
        if self.args.run:
            self.run()
        if self.args.post_process:
            self.post_process()
        if self.args.compare:
            self.compare()


def __main__():
    npb_runner = NPBRunner()
    npb_runner.dispatch()


if __name__ == "__main__":
    __main__()
