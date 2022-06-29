#!/usr/bin/env python3

import argparse
import logging
import sys

sys.path.append("/bulk/wb/unasl-project/UnASL/migration/lib/core/")

import coredump
import elf

import lief

logger = logging.getLogger("ELF coredump transform")
logger.setLevel(logging.DEBUG)


def xform_core(input_core, input_exec, output_exec, output_core_name):
    gen = coredump.coredump_generator()
    gen.input_core = input_core
    gen.input_executable = input_exec
    gen.output_executable = output_exec

    gen()

    gen.write(".")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ELF Coredump transform")
    parser.add_argument(
        "--core", "-c", default="", help="Input core to transform"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="dump-xformed.core",
        help="Output corefile name. (Default: %(default)",
    )
    parser.add_argument(
        "--executables", "-x", nargs=2, help="x86_64 and AArch64 executables"
    )
    args = parser.parse_args()

    core = lief.parse(args.core)
    if not (
        isinstance(core, lief.ELF.Binary)
        and core.header.file_type == lief.ELF.E_TYPE.CORE
    ):
        logger.error(f"{args.core} is not an ELF Core file")
        exit(1)

    bin0 = lief.parse(args.executables[0])

    if not (
        isinstance(bin0, lief.ELF.Binary)
        and bin0.header.file_type == lief.ELF.E_TYPE.EXECUTABLE
    ):
        logger.error(f"{args.executables[0]} is not an ELF Executable file")
        exit(1)

    bin1 = lief.parse(args.executables[1])

    if not (
        isinstance(bin1, lief.ELF.Binary)
        and bin1.header.file_type == lief.ELF.E_TYPE.EXECUTABLE
    ):
        logger.error(f"{args.executables[1]} is not an ELF Executable file")
        exit(1)

    if bin0.header.machine_type == bin1.header.machine_type:
        logger.error(
            f"ELF Executable files cannot be the same arch: {bin0.header.machine_type}"
        )
        exit(1)

    x86bin = bin0
    armbin = bin1

    if bin0.header.machine_type == lief.ELF.ARCH.AARCH64:
        x86bin = bin1
        armbin = bin0

    # input_core_json = lief.to_json(core)

    if core.header.machine_type == lief.ELF.ARCH.AARCH64:
        xform_core(
            input_core=core,
            input_exec=armbin,
            output_exec=x86bin,
            output_core_name=args.output,
        )
    else:
        logger.warning(
            "ELF Core conversion from x86_64 to AArch64 is not implemented."
        )
