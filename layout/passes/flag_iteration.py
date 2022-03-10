#!/usr/bin/env python3

import argparse
import os
import subprocess
import shlex


def execute_bash_command(bash_cmd):
    """
    Executes a bash command and prints potential errors.

    :return:
    """
    process = subprocess.Popen(shlex.split(bash_cmd),
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output, error = process.communicate()

    return output, error, process.returncode


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
        for y in seq[start_point:]:
            yield x + ' ' + y
        start_point += 1


def flag_iteration(flag_file, src_dir, tool, flag_num=1, verbose=False):
    """
    Iterate over LLVM flags using Makefile, running stackmaps-check.
    Assumes that each flag is in a separate line.

    @param flag_file: list of flags
    @param src_dir: Where to run the commands (assumes it is a subdir of layout/)
    @param tool: Which LLVM tool are we using to test its flags
    @param flag_num: How many combinations of flags to try (currently 1 or 2 are supported)
    @param verbose: Whether to print Makefile output
    @return:
    """
    tool_flags = {
        'clang': 'CLANG_FLAGS',
        'opt': 'OPT_FLAGS',
        'llc': 'LLC_FLAGS',
    }

    flags = flag_file.read()
    flags = flags.split('\n')[:-1]  # Assumes flag file ends with empty line

    if flag_num == 2:
        flags = cartesian_product(flags)

    for flag_combo in flags:
        os.chdir(src_dir)

        execute_bash_command('make clean')
        cmd = 'make stackmaps-check {}="{}"'.format(tool_flags[tool],
                                                    flag_combo)
        output, error, ret_code = execute_bash_command(cmd)
        if ret_code == 0:
            print('SUCCESS:', flag_combo)
        elif verbose:
            print(error.decode('utf-8'))

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
    parser.add_argument('-v',
                        '--verbose',
                        action='store_true',
                        required=False,
                        default=False)

    args = parser.parse_args()

    flag_iteration(flag_file=args.flags_file,
                   src_dir=args.src_dir,
                   tool=args.llvm_tool,
                   flag_num=args.flag_num,
                   verbose=args.verbose)
