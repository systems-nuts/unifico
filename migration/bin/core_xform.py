#!/usr/bin/env python3

import argparse
import sys

sys.path.append('/bulk/wb/unasl-project/UnASL/migration/lib/core/')

import coredump
import elf

import lief


def xform_x86_to_arm(input_core_json, x86bin, armbin, output):
    gen = coredump.coredump_generator()
    gen.input_core = input_core_json

    gen()

    gen.write(".")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ELF Coredump transform")
    parser.add_argument("--core", "-c", default="", help="")
    parser.add_argument(
        "--output",
        "-o",
        default="dump-xformed.core",
        help="Output corefile name. (Default: %(default)",
    )
    parser.add_argument("-x", help="x86 executable")
    parser.add_argument("-a", help="Aarch64 executable")
    args = parser.parse_args()

    core = lief.parse(args.core)
    x86bin = lief.parse(args.x)
    armbin = lief.parse(args.a)

    assert isinstance(core, lief.ELF.Binary)
    assert isinstance(x86bin, lief.ELF.Binary)
    assert isinstance(armbin, lief.ELF.Binary)

    assert core.header.file_type == lief.ELF.E_TYPE.CORE
    assert x86bin.header.file_type == lief.ELF.E_TYPE.EXECUTABLE
    assert armbin.header.file_type == lief.ELF.E_TYPE.EXECUTABLE

    assert x86bin.header.machine_type == lief.ELF.ARCH.x86_64
    assert armbin.header.machine_type == lief.ELF.ARCH.AARCH64

    input_core_json = lief.to_json(core)

    xform_x86_to_arm(input_core_json, x86bin, armbin, args.output)
