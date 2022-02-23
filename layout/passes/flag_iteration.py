#!/usr/bin/env python3

import argparse
import os
import subprocess


def execute_bash_command(bash_cmd):
    """
    Executes a bash command and prints potential errors.

    :return:
    """
    process = subprocess.Popen(bash_cmd.split(),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL)
    process.communicate()
    return process.returncode


def powerset(seq):
    """
    Returns all the subsets of this set. This is a generator.
    From: https://stackoverflow.com/a/1482322/9683118
    We can use this to test combinations of a (small) set of flags.

    @param seq: A sequence of flags
    @return: A generator
    """
    if len(seq) <= 1:
        yield seq
        yield []
    else:
        for item in powerset(seq[1:]):
            yield [seq[0]] + item
            yield item


def cartesian_product(seq):
    """
    Returns the cartesian product seq x seq.
    Omits all pairs with the same elements.
    Useful to test combinations of two flags.

    @param seq: A sequence of flags
    @return: A generator
    """
    start_point = 1
    for x in seq:
        start_point += 1
        for y in seq[start_point:]:
            yield x + ' ' + y


def flag_iteration(flag_file, src_dir, tool, flag_num=1):
    """
    Iterate over LLVM flags using Makefile, running stackmaps-check.
    Assumes that each flag is in a separate line.

    @param flag_file: list of flags
    @param src_dir: Where to run the commands (assumes it is a subdir of layout/)
    @param tool: Which LLVM tool are we using to test its flags
    @param flag_num: How many combinations of flags to try (currently 1 or 2 are supported)
    @return:
    """
    tool_flags = {
        'clang': 'EXTRA_CLANG_FLAGS',
        'opt': 'EXTRA_OPT_FLAGS',
        'llc': 'EXTRA_LLC_FLAGS',
    }

    flags = flag_file.read()
    flags = flags.split('\n')[:-1]  # Assumes flag file ends with empty line

    if flag_num == 2:
        flags = cartesian_product(flags)

    for flag_combo in flags:
        os.chdir(src_dir)

        execute_bash_command('make clean')
        ret_code = execute_bash_command('make stackmaps-check {}={}'.format(
            tool_flags[tool], flag_combo))
        if ret_code == 0:
            print('SUCCESS:', flag_combo)

        os.chdir('..')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=
        'A script to iterate over LLVM flags. Run it inside unified_abi/layout/'
    )

    parser.add_argument('-f', '--flags-file', type=argparse.FileType('r'))
    parser.add_argument('-s', '--src-dir', type=str)
    parser.add_argument('-t',
                        '--llvm-tool',
                        type=str,
                        required=False,
                        choices=['clang', 'opt', 'llc'],
                        default='opt')
    parser.add_argument('-n',
                        '--flag-num',
                        type=int,
                        required=False,
                        default=1)

    args = parser.parse_args()

    flag_iteration(flag_file=args.flags_file,
                   src_dir=args.src_dir,
                   tool=args.llvm_tool,
                   flag_num=args.flag_num)
