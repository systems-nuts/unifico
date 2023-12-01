import subprocess
import argparse
import os
import sys
import json
from datetime import datetime
from pin_postprocess.plot_accesses import scatter_csv_plot
from pathlib import Path

OBJ_DIR = "obj-intel64"
OUT_DIR = "out"
JSON_LOG = "out.log"
AWK_CMD = 'awk \'($2 == "T" || $2 == "t") && $1 {print "b " $1}\' '
SED_CMD1 = "sed 's/\.[^ ]*//g'"
SED_CMD2 = "sed 's/\\ /,/g'"
EMPTY_THRESHOLD = 10


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
        self.unknown_args.remove("--")
        if self.args.all_functions:
            cmd = f"nm -P {self.args.app_path} | {SED_CMD1} | {AWK_CMD} | cut -c2- | xargs | {SED_CMD2}"
            if self.args.dry_run:
                print(cmd)
                print(self.execute_bash_command(cmd))
            self.args.functions = self.execute_bash_command(cmd)
            self.args.functions = self.args.functions.rstrip()
        self.granularity = eval(self.args.granularity)

    def log(self, out_dir):
        log_dict = vars(self.args)
        if self.unknown_args:
            unknown_args = "_".join(self.unknown_args)
            log_dict["unknown_args"] = unknown_args
        json_file = os.path.join(out_dir, JSON_LOG)
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(log_dict, f, ensure_ascii=False, indent=4)

    def run(self):
        os.chdir(self.args.tool_dir)
        access_type = (
            "heap_accesses"
            if not self.args.stack_profile
            else "stack_accesses"
        )
        now = datetime.now()
        time_stamp = now.strftime("%Y%m%d") + "_" + now.strftime("%H%M%S")
        out_dir = os.path.join(OUT_DIR, self.args.app_name, time_stamp)
        Path(out_dir).mkdir(parents=True, exist_ok=False)

        self.log(out_dir)

        for func_name in self.args.functions.split(","):
            print(func_name)
            csv_file = os.path.join(out_dir, func_name + ".csv")
            png_file = os.path.join(out_dir, func_name + ".png")

            cmd = (
                f"{self.pin_path} -t {OBJ_DIR}/{self.args.tool} -o {csv_file} -f {func_name} "
                f"{'-s' if self.args.stack_profile else ''} -g {self.granularity} "
                f"-- {self.args.app_path} {' '.join(self.unknown_args)}"
            )
            if self.args.dry_run:
                print(cmd)
                return
            self.execute_bash_command(cmd)

            num_lines = sum(1 for _ in open(csv_file))
            # If a csv file has less than certain points, the plot will look empty.
            if num_lines < EMPTY_THRESHOLD:
                continue

            scatter_csv_plot(csv_file, png_file, self.args.keep_csv)

    @staticmethod
    def cmd_line_arguments(arg_parser: argparse.ArgumentParser):
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
            "--all-functions",
            required=False,
            action="store_true",
            default=False,
        )
        arg_parser.add_argument(
            "-s", "--stack-profile", required=False, action="store_true"
        )
        arg_parser.add_argument(
            "--dry-run", required=False, action="store_true"
        )
        arg_parser.add_argument(
            "--keep-csv", required=False, action="store_true"
        )
        arg_parser.add_argument(
            "-g", "--granularity", required=False, default="0", type=str
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
