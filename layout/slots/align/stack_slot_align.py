#!/usr/bin/env python3

import sys
import re
import json

FUNCTION_REGEX = re.compile(
    r"""
    \*+
 \s         # A whitespace
 Function:
 \s         # A whitespace
    (\w+)   # Function name
    .*      # Ignore rest
    """,
    re.VERBOSE,
)

SLOT_REGEX = re.compile(
    r"""
 Assigning
 \s         # A whitespace
 fi\#(\d+)    # Original slot
 \s         # A whitespace
 to
 \s         # A whitespace
 fi\#\d+  # New slot
 \s         # A whitespace
 align
 \s         # A whitespace
 (\d+)      # alignment
 .*         # Ignore rest
""",
    re.VERBOSE,
)


def get_stack_slots(stack_slot_output):
    """Parse the output of stack slot coloring debug output and return a dictionary with the stack slots and
    alignments per function.

    Given a stack slot coloring debug output, iterate over all functions.
    Return a dictionary with the alignment of all stack slots inside each function.
    Example:

    INPUT:

    ********** Stack Slot Coloring **********
    ********** Function: results
    Spill slot intervals:
    SS#0 [320r,432r:0)  0@x weight:2.000000e+00

    Color spill slot intervals:
    Assigning fi#0 to fi#0 align 8 size 8

    Spill slots after coloring:
    SS#0 [320r,432r:0)  0@x weight:2.000000e+00

    ********** Stack Slot Coloring **********
    ********** Function: main

    OUTPUT:

        {
            "results": {
            "0": 16
        },
            "main": {}
        }

        @param stack_slot_output: Text file
        @return: dictionary
    """
    result = {}

    with open(stack_slot_output, "r") as objdump_file:
        lines = objdump_file.readlines()

        for index, line in enumerate(lines):
            match_result = FUNCTION_REGEX.match(line)

            if match_result:  # Inside a function
                cur_function = match_result.group(1)
                result[cur_function] = {}
                continue

            match_result2 = SLOT_REGEX.match(line)

            if match_result2:
                stack_slot = match_result2.group(1)
                alignment = match_result2.group(2)
                result[cur_function][stack_slot] = int(alignment)
                continue

    return result


def check_stack_slot_number(d1, d2):
    """Verify that both dictionaries have the same number of stack slots per function.

    Given two stack slot dictionaries, verify that they contain the same functions,
    and each function has the same number of stack slots.
    A stack slot dictionary has the following form:

    { 'add': { '0': 16, }, 'main': { '0': 8, '1': 16 } }

    @param d1: stack slot dictionary
    @param d2: stack slot dictionary
    @return: Return true iff verification was successful, otherwise either exit with failure in the case
    of different functions or return false in the case of different number of stack slots per function.
    """
    if d1.keys() != d2.keys():
        print("Error: Different number of functions.", file=sys.stderr)
        print("aarch64 `set difference` x86-64: ", file=sys.stderr)
        print(set(d1.keys()) - set(d2.keys()), file=sys.stderr)
        print("x86-64 `set difference` aarch64: ", file=sys.stderr)
        print(set(d2.keys()) - set(d1.keys()), file=sys.stderr)
        exit(1)

    for function in d1.keys():
        stack_slots1 = d1[function]
        stack_slots2 = d2[function]

        if stack_slots1.keys() != stack_slots2.keys():
            print(
                "WARNING: Different number of stack slots in function `{}`.".format(
                    function
                ),
                file=sys.stderr,
            )
            print("aarch64 `set difference` x86-64: ", file=sys.stderr)
            print(
                set(stack_slots1.keys()) - set(stack_slots2.keys()),
                file=sys.stderr,
            )
            print("x86-64 `set difference` aarch64: ", file=sys.stderr)
            print(
                set(stack_slots2.keys()) - set(stack_slots1.keys()),
                file=sys.stderr,
            )
            return False

    return True


def align_stack_slots(text1, text2):
    """Return the stack slot padding for two different stack slot coloring debug outputs.

    @param text1: stack slot coloring debug output input for arm
    @param text2: stack slot coloring debug output input for x86
    @return: Padding dictionary or 1 in the case of failure
    """
    d1 = get_stack_slots(text1)
    d2 = get_stack_slots(text2)

    padding_dict = {}

    # TODO: Remove duplication with callsite_align.py
    # Perhaps this check will have already been done in callsite_align.py
    if d1.keys() != d2.keys():
        print("Error: Different number of functions.", file=sys.stderr)
        print("aarch64 `set difference` x86-64: ", file=sys.stderr)
        print(set(d1.keys()) - set(d2.keys()), file=sys.stderr)
        print("x86-64 `set difference` aarch64: ", file=sys.stderr)
        print(set(d2.keys()) - set(d1.keys()), file=sys.stderr)
        exit(1)

    for function in d1.keys():
        padding_dict[function] = {}
        if list(d1[function].keys()) != list(d2[function].keys()):
            print(
                f"WARNING: Different stack slot numbering in function `{function}`.",
                file=sys.stderr,
            )
            continue
        for stack_slot in d1[function].keys():
            # We are not adamant about the same stack slot number in both functions
            # Try your luck in the next function
            if d1[function].keys() != d2[function].keys():
                continue
            # Maximum alignment between the same slot in both architectures
            alignment = max(d1[function][stack_slot], d2[function][stack_slot])
            padding_dict[function][stack_slot] = alignment

    print(json.dumps(padding_dict, indent=4))
    return padding_dict


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: ./stack_slot_align <objdump_input_arm> <objdump_input_x86>"
        )
        sys.exit(1)

    align_stack_slots(sys.argv[1], sys.argv[2])
