#!/usr/bin/env python3

import sys
import re
import json

# TODO fix return behaviour to use return values (failure exit should be
# invoked by script code).
# TODO move script commandline code to main script at the top-level of this
# module

# This verbose and more readable regex form, requires the re.VERBOSE flag in re.compile
FUNCTION_REGEX = re.compile(
    r"""
 \d+        # Function symbol address
 \s         # A whitespace
 <?(\w+)>?: # Function name, optionally enclosed in '<...>'
 .*         # Ignore rest
""",
    re.VERBOSE,
)

# Will be used with re.search
CALLSITE_REGEX = {"x86-64": r"\s(callq?)\s", "aarch64": r"\s(bl)\s"}

RETURN_ADDRESS_REGEX = re.compile(
    r"""
 \s*                # Initial whitespaces
 ([0-9a-fA-F]+):    # Hex offset
 .*                 # Ignore rest
""",
    re.VERBOSE,
)


def get_return_addresses(objdump_output, arch):
    """Parse the output of `objdump` and return a dictionary with the return addresses per function.

        Given an objdump output, iterate over all functions.
        Return a dictionary with the return addresses of all callsites inside each function.
        Example:

        INPUT:

    0000000000000000 <add_7>:
       0:	d100c3ff 	sub	sp, sp, #0x30
        ...
      (no calls inside add_7)
        ...
      40:	d65f03c0 	ret

    0000000000000044 <main>:
      44:	d100c3ff 	sub	sp, sp, #0x30
        ...
      84:	97ffffdf 	bl	0 <add_7>
      88:	90000000 	adrp	x0, 0 <add_7>
        ...
      98:	94000000 	bl	0 <printf>
      9c:	a9427bfd 	ldp	x29, x30, [sp, #32]
        ...
      a8:	d65f03c0 	ret

        OUTPUT:

        {
            ".Lmain0": "88",
            ".Lmain1": "9c"
        }

        where we follow the naming convention of temporary labels as emitted by LLVM at callsites.
        @param objdump_output: Text file
        @param arch: x86-64 or aarch64
        @return: dictionary
    """
    result = {}

    with open(objdump_output, "r") as objdump_file:
        lines = objdump_file.readlines()

        for index, line in enumerate(lines):
            match_result = FUNCTION_REGEX.match(line)

            if match_result:  # Inside a function's code
                counter = 0
                cur_function = match_result.group(1)
                result[cur_function] = {}
                continue

            match_result2 = re.search(CALLSITE_REGEX[arch], line)

            if match_result2:  # Found a call instruction
                nextLine = lines[index + 1]
                match_result3 = RETURN_ADDRESS_REGEX.match(
                    nextLine
                )  # Parsing instruction after the call

                if not match_result3:
                    print("Unreachable")
                else:
                    cur_label = ".L" + cur_function + str(counter)
                    result[cur_function][cur_label] = match_result3.group(1)
                    counter = counter + 1

    return result


def check_callsite_number(d1, d2):
    """Verify that both dictionaries have the same number of callsites per function.

    Given to callsite dictionaries, verify that they contain the same functions,
    and each function has the same number of callsites.
    A callsite dictionary has the following form:

    {
        'add': {
            '.Ladd0': 12,
        },
        'main': {
            '.Lmain0': 2,
            '.Lmain1': 1
        }
    }
    @param d1: callsite dictionary
    @param d2: callsite dictionary
    @return: Return iff verification was successful, otherwise exit with failure
    """
    if d1.keys() != d2.keys():
        print("Error: Different number of functions.", file=sys.stderr)
        print("aarch64 `set difference` x86-64: ", file=sys.stderr)
        print(set(d1.keys()) - set(d2.keys()), file=sys.stderr)
        print("x86-64 `set difference` aarch64: ", file=sys.stderr)
        print(set(d2.keys()) - set(d1.keys()), file=sys.stderr)
        exit(1)

    for function in d1.keys():
        callsites1 = d1[function]
        callsites2 = d2[function]

        if callsites1.keys() != callsites2.keys():
            print(
                "Error: Different number of callsites in function `{}`.".format(
                    function
                ),
                file=sys.stderr,
            )
            print("aarch64 `set difference` x86-64: ", file=sys.stderr)
            print(
                set(callsites1.keys()) - set(callsites2.keys()),
                file=sys.stderr,
            )
            print("x86-64 `set difference` aarch64: ", file=sys.stderr)
            print(
                set(callsites2.keys()) - set(callsites1.keys()),
                file=sys.stderr,
            )
            exit(1)

    return


def align(text1, text2):
    """Return the callsite padding as a lit for two different objdump outputs.

    Get a clean output of objdump by keeping only line of the .text section that have calls.
    Calculate the necessary padding for the architectures (currently x86-64 and ARM-v8 supported).
    For x86-64 call instructions should end at a 4-byte boundary. See: TODO

    https://stackoverflow.com/questions/67578127/align-x86-64-and-aarch64-callsites

    Aarch64 instructions should be 4-byte aligned.

    @param text1: objdump input for arm-v8
    @param text2: objdump input for x86-64
    @return: Padding dictionary or 1 in the case of failure
    """
    d1 = get_return_addresses(text1, "aarch64")
    d2 = get_return_addresses(text2, "x86-64")

    check_callsite_number(d1, d2)

    padding_dict = {"aarch64": {}, "x86-64": {}}
    for function in d1.keys():
        # Accumulated paddings for each function in both architectures
        total_padding_arm = 0
        total_padding_x86 = 0

        for label in d1[function].keys():
            # Offsets of call instructions from the caller function's symbol
            offset_arm = int(d1[function][label], 16) + total_padding_arm
            offset_x86 = int(d2[function][label], 16) + total_padding_x86

            diff = offset_x86 - offset_arm
            padding_x86 = 0
            padding_arm = 0

            if diff < 0:
                padding_x86 = abs(
                    diff
                )  # We assume that x86-64 can be padded arbitrarily...
                padding_arm = 0

            if diff > 0:
                if (
                    diff % 4 == 0
                ):  # ...whereas we know that arm-v8 instructions must be 4-byte aligned
                    padding_arm = diff
                else:
                    padding_x86 = 4 - diff % 4
                    padding_arm = 4 * (diff // 4 + 1)

            padding_dict["aarch64"][label] = padding_arm
            padding_dict["x86-64"][label] = padding_x86
            total_padding_arm = total_padding_arm + padding_arm
            total_padding_x86 = total_padding_x86 + padding_x86

    print(json.dumps(padding_dict, indent=4))
    return padding_dict


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: ./callsite_align <objdump_input_arm> <objdump_input_x86>"
        )
        sys.exit(1)

    align(sys.argv[1], sys.argv[2])
