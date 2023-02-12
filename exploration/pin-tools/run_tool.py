import subprocess
import argparse
import os
import sys
from pin_postprocess.plot_accesses import plot_scatter_df
from pathlib import Path

OBJ_DIR = "obj-intel64"
PLOT_DIR = "plots/"
CSV_DIR = "csv/"
AWK_CMD = 'awk \'$2 == "T" && $1 !~ /^_/ {print "b " $1}\' '
SED_CMD = "sed 's/\ /,/g'"


class PinToolRunner:
    args: argparse.Namespace
    """
    The argument parsers namespace which holds the parsed commandline
    attributes.
    """

    def __init__(self, args=None):
        arg_parser = argparse.ArgumentParser(
            description="A runner class for Intel's Pin Tools"
        )
        self.pin_path = os.environ.get("PIN_PATH")
        if not self.pin_path:
            sys.exit("Error: Please set Pin location path (PIN_PATH)")
        self.cmd_line_arguments(arg_parser)
        self.args, self.unknown_args = arg_parser.parse_known_args(args=args)
        if self.args.all_functions:
            cmd = f"nm -P {self.args.app_path} | {AWK_CMD} | cut -c2- | xargs | {SED_CMD}"
            if self.args.dry_run:
                print(cmd)
                print(self.execute_bash_command(cmd))
                return
            self.args.functions = self.execute_bash_command(cmd)
            self.args.functions = self.args.functions.rstrip()

    def run(self):
        os.chdir(self.args.tool_dir)
        access_type = (
            "heap_accesses"
            if not self.args.stack_profile
            else "stack_accesses"
        )
        for func_name in self.args.functions.split(","):

            out_file_stem = f"{self.args.app_name}_{func_name}_{self.args.granularity}_{access_type}"
            Path(os.path.join(CSV_DIR, self.args.app_name)).mkdir(
                parents=True, exist_ok=True
            )
            Path(os.path.join(PLOT_DIR, self.args.app_name)).mkdir(
                parents=True, exist_ok=True
            )

            csv_file = os.path.join(
                CSV_DIR, self.args.app_name, out_file_stem + ".csv"
            )
            png_file = os.path.join(
                PLOT_DIR, self.args.app_name, out_file_stem + ".png"
            )

            cmd = (
                f"{self.pin_path} -t {OBJ_DIR}/{self.args.tool} -o {csv_file} -f {func_name} "
                f"{'-s' if self.args.stack_profile else ''} -g {self.args.granularity} "
                f"-- {self.args.app_path} {' '.join(self.unknown_args)}"
            )
            if self.args.dry_run:
                print(cmd)
                return
            self.execute_bash_command(cmd)
            plot_scatter_df(csv_file, png_file)

    def cmd_line_arguments(self, arg_parser: argparse.ArgumentParser):
        """
        Registers all the command line arguments that are used by this tool.

        Add other/additional arguments by overloading this function.
        """
        arg_parser.add_argument("-a", "--app-path", required=True, type=str)
        arg_parser.add_argument("--app-name", required=True, type=str)
        arg_parser.add_argument("-t", "--tool", required=True, type=str)
        arg_parser.add_argument("-d", "--tool-dir", required=True, type=str)
        arg_parser.add_argument("-f", "--functions", required=False, type=str)
        arg_parser.add_argument(
            "--all-functions", required=False, action="store_true"
        )
        arg_parser.add_argument(
            "-s", "--stack-profile", required=False, action="store_true"
        )
        arg_parser.add_argument(
            "--dry-run", required=False, action="store_true"
        )
        arg_parser.add_argument(
            "-g", "--granularity", required=False, default=0, type=int
        )

    @staticmethod
    def execute_bash_command(bash_cmd):
        """
        Executes a bash command and prints potential errors.

        :return:
        """
        process = subprocess.Popen(
            bash_cmd, shell=True, stdout=subprocess.PIPE
        )
        output, error = process.communicate()
        if error:
            print("Error: ", error)
        return output.decode(encoding="utf-8")


if __name__ == "__main__":
    pin_tool_runner = PinToolRunner()
    pin_tool_runner.run()
