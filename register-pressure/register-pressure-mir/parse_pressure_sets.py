#!/usr/bin/env python3

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


def get_pressure_sets(
    input_file, function_block, machine_instruction, skip_if
):
    """
    Get the pressure sets at a specific LLVM Machine Instruction (if given),
    from the particular function block, e.g.,

    `%18:gr64_nosp = MOV64rm %stack.3.i, 1, $noreg, 0, $noreg` of `main:%bb.2 for.body`

    If a Machine Instruction is not given, return the pressure sets for all possible MIs of the block.
    The input file is the output of the `machine-scheduler` pass.

    @param input_file: Path to debug output file
    @param function_block: E.g., loop:%bb.0
    @param machine_instruction: LLVM MI, e.g., `MOV32mi %stack.0.retval, 1, $noreg, 0`
    @param skip_if: Whether we skip the `if` block
    @return: List of Dictionaries with pressure sets
    """
    with open(input_file, "r") as objdump_file:
        lines = objdump_file.readlines()

        start_counting = False
        skip_function = True
        skip_instruction = True
        pressure_sets = {}
        pressure_sets_list = {}

        for index, line in enumerate(lines):
            if line.find(":%bb.") != -1:
                block_name = line
                if function_block and not line.startswith(function_block):
                    skip_function = True

            if line.find("From:") != -1:
                block_name += line

            if line.find("To:") != -1:
                block_name += line

            if not function_block or line.startswith(function_block):
                # skip the `if`
                if not skip_if or (skip_if and line.find(" if.") == -1):
                    skip_function = False

            if (
                not skip_function
                and machine_instruction
                and machine_instruction in line
            ):
                skip_instruction = False
            elif not skip_function and not function_block:
                skip_instruction = False
            elif not skip_function and not machine_instruction:
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
                class_name = match_result.group(2)
                class_name = class_name.replace(
                    "GPR", "GR"
                )  # To align the naming between X86 and AArch64.
                pressure_sets[class_name] = int(match_result.group(3))
                continue

            if line.startswith("Live In:"):
                if len(pressure_sets) != 0:
                    pressure_sets_list.update({block_name: pressure_sets})
                pressure_sets = {}
                start_counting = False
                skip_function = True
                skip_instruction = True

    return pressure_sets_list


def calculate_pressure(pressure_sets):
    """
    Given a dictionary with pressure sets, calculate the total register pressure.
    Currently, focusing on 32- and 64-bit registers.

    @param pressure_sets: dict
    @return: register pressure as a number
    """
    pressure = 0

    # if pressure_sets.get("GR8"): TODO: ignore for now
    #     pressure += pressure_sets["GR8"]

    # if pressure_sets.get("GR16"):
    #     pressure += pressure_sets["GR16"]

    if pressure_sets.get("GR32"):
        pressure += pressure_sets["GR32"]
    elif pressure_sets.get("GR32common"):
        pressure += pressure_sets["GR32common"]
    elif pressure_sets.get("GR32temp"):
        pressure += pressure_sets["GR32temp"]
    elif pressure_sets.get("GR32_TC"):
        pressure += pressure_sets["GR32_TC"]

    if pressure_sets.get("GR64"):
        pressure += pressure_sets["GR64"]
    elif pressure_sets.get("GR64common"):
        pressure += pressure_sets["GR64common"]
    elif pressure_sets.get("GR64temp"):
        pressure += pressure_sets["GR64temp"]
    elif pressure_sets.get("GR64_TC"):
        pressure += pressure_sets["GR64_TC"]
    elif pressure_sets.get("GR64_TCW64"):
        pressure += pressure_sets["GR64_TCW64"]

    if pressure_sets.get("FR32X"):
        pressure += pressure_sets["FR32X"]

    if pressure_sets.get("FR64X"):
        pressure += pressure_sets["FR64X"]

    return pressure


arg_parser = argparse.ArgumentParser(
    description="Register pressure calculator at the MIR level."
)

arg_parser.add_argument(
    "-i", "--input_file", type=str, nargs="?", help="Path to input file"
)

arg_parser.add_argument(
    "-o", "--output_file", type=str, nargs="?", help="Path to output file"
)

arg_parser.add_argument(
    "-b", "--basic_block", type=str, nargs="?", help="Basic block name"
)

arg_parser.add_argument(
    "-m",
    "--machine_instruction",
    type=str,
    nargs="?",
    help="Machine instruction name",
)

arg_parser.add_argument(
    "-s", "--skip_if", type=bool, default=False, help="Skip the if-block"
)


def __main__(args: argparse.Namespace):
    pressure_sets_list = get_pressure_sets(
        args.input_file,
        args.basic_block,
        args.machine_instruction,
        args.skip_if,
    )
    if len(pressure_sets_list) == 0:
        return
    max_block = max(
        pressure_sets_list.items(),
        key=lambda item: calculate_pressure(item[1]),
    )
    block_name, pressure_sets = max_block
    max_pressure = calculate_pressure(pressure_sets)
    print(block_name, "with: ", max_pressure)


if __name__ == "__main__":
    args = arg_parser.parse_args()
    __main__(args)
