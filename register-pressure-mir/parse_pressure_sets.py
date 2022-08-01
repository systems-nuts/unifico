import argparse
import re

# The debug output of `machine-scheduler` is expected as an input.
# The following lines are detected and parsed:

# Max Pressure: GR32_BPSP=1
# GR32_SIDI=1
# GR32_DIBP+GR32_SIDI=1
# GR32_DIBP+LOW32_ADDR_ACCESS_with_sub_32bit=1
# GR64_NOREX=1
# GR8=1
# GR8+GR32_DIBP=1
# GR8+GR32_BSI=1
# GR64_TC+GR64_TCW64=1
# GR8+LOW32_ADDR_ACCESS_with_sub_32bit=1
# ...
#
# We parse the values in the right-hand side of the equalities.
# TODO: How to calculate pressure, considering the class overlaps?


# This verbose and more readable regex form, requires the re.VERBOSE flag in re.compile


# This verbose and more readable regex form, requires the re.VERBOSE flag in re.compile
REG_CLASS_REGEX = re.compile(
    r"""
    (Max\sPressure:\s)? # First appearing class starts with this
 ([\w+]+)=     # Presure set name
 (\d+)        # Set pressure
 .*         # Ignore rest
""",
    re.VERBOSE,
)

arg_parser = argparse.ArgumentParser(
    description="Register pressure calculator at the MIR level."
)

arg_parser.add_argument(
    "-i", "--input_file", type=str, nargs="?", help="Path to input file"
)

arg_parser.add_argument(
    "-o", "--output_file", type=str, nargs="?", help="Path to output file"
)


def __main__(args: argparse.Namespace):
    with open(args.input_file, "r") as objdump_file:

        lines = objdump_file.readlines()

        start_counting = False

        for index, line in enumerate(lines):

            if line.startswith("Max Pressure:"):
                start_counting = True

            match_result = REG_CLASS_REGEX.match(line)
            if match_result and start_counting:  # Inside a function's code
                print(match_result.group(0))
                continue

            if line.startswith("Live In:"):
                start_counting = False
                print("-------")


if __name__ == "__main__":
    args = arg_parser.parse_args()
    __main__(args)
