import argparse
import re

# The debug output of `machine-scheduler` is expected as an input.
# The following lines are detected and parsed:
#
# main:%bb.2 for.body
#   From: %18:gr64_nosp = MOV64rm %stack.3.i, 1, $noreg, 0, $noreg :: (dereferenceable load 8 from %ir.i)
# ...
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


REG_CLASS_REGEX = re.compile(
    r"""
    (Max\sPressure:\s)? # First appearing class starts with this
 ([\w+]+)=     # Presure set name
 (\d+)        # Set pressure
 .*         # Ignore rest
""",
    re.VERBOSE,
)


def get_pressure_sets(input_file, function_block, machine_instruction):
    """
    Get the pressure sets at a specific LLVM Machine Instruction,
    from the particular function block, e.g.,

    `%18:gr64_nosp = MOV64rm %stack.3.i, 1, $noreg, 0, $noreg` of `main:%bb.2 for.body`

    The input file is the output of the `machine-scheduler` pass.

    @param input_file: Path to debug output file
    @param function_block: E.g., loop:%bb.0
    @param machine_instruction: LLVM MI, e.g., `MOV32mi %stack.0.retval, 1, $noreg, 0`
    @return: Dictionary with pressure sets
    """
    with open(input_file, "r") as objdump_file:
        lines = objdump_file.readlines()

        start_counting = False
        skip_function = True
        skip_instruction = True
        pressure_sets = {}

        for index, line in enumerate(lines):

            if line.startswith(function_block):
                skip_function = False

            if machine_instruction in line:
                skip_instruction = False

            if line.startswith("Max Pressure:"):
                start_counting = True

            match_result = REG_CLASS_REGEX.match(line)
            if (
                match_result
                and not skip_function
                and not skip_instruction
                and start_counting
            ):
                pressure_sets[match_result.group(2)] = match_result.group(3)
                continue

            if line.startswith("Live In:"):
                start_counting = False
                skip_function = True
                skip_instruction = True

    return pressure_sets


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
    pressure_sets = get_pressure_sets(
        args.input_file,
        "main:%bb.2 for.body",
        "%18:gr64_nosp = MOV64rm %stack.3.i, 1, $noreg, 0, $noreg",
    )
    print(pressure_sets)


if __name__ == "__main__":
    args = arg_parser.parse_args()
    __main__(args)
