import subprocess
import argparse
import os
import sys
from pin_postprocess.plot_accesses import plot_scatter_df

OBJ_DIR = "obj-intel64"


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
        self.args = arg_parser.parse_args(args=args)

    def run(self):
        os.chdir(self.args.tool_dir)
        cmd = f"{self.pin_path} -t {OBJ_DIR}/{self.args.tool} -o {self.args.csv_name} -f {self.args.function} {'-s' if self.args.stack_profile else ''} -g {self.args.granularity} -- {self.args.app} "
        self.execute_bash_command(cmd)
        plot_scatter_df(self.args.csv_name, self.args.plot_name)

    def cmd_line_arguments(self, arg_parser: argparse.ArgumentParser):
        """
        Registers all the command line arguments that are used by this tool.

        Add other/additional arguments by overloading this function.
        """
        arg_parser.add_argument("-a", "--app", required=True, type=str)
        arg_parser.add_argument("-t", "--tool", required=True, type=str)
        arg_parser.add_argument("-d", "--tool-dir", required=True, type=str)
        arg_parser.add_argument("-f", "--function", required=True, type=str)
        arg_parser.add_argument(
            "-s", "--stack-profile", required=False, action="store_true"
        )
        arg_parser.add_argument(
            "-g", "--granularity", required=False, default=0, type=int
        )
        arg_parser.add_argument(
            "-c",
            "--csv-name",
            required=False,
            default="memory_accesses.csv",
            type=str,
        )
        arg_parser.add_argument(
            "-p",
            "--plot-name",
            required=False,
            default="memory_accesses.png",
            type=str,
        )

    @staticmethod
    def execute_bash_command(bash_cmd):
        """
        Executes a bash command and prints potential errors.

        :return:
        """
        process = subprocess.Popen(bash_cmd.split(), stdout=subprocess.PIPE)
        _, error = process.communicate()
        if error:
            print("Error: ", error)


if __name__ == "__main__":
    pin_tool_runner = PinToolRunner()
    pin_tool_runner.run()
