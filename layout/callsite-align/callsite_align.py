import sys
import re
import json

FUNCTION_REGEX = r'\d+\s(\w+):.*'
CALLSITE_REGEX = {
    'x86-64': r'\s(callq)\s',
    'aarch64': r'\s(bl)\s'
}
RETURN_ADDRESS_REGEX = r'\s*(\w\w):.*'


def get_return_addresses(objdump_output, arch):
    """ Parse the output of `objdump` and return a dictionary with the return addresses per function.

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

            match_result = re.match(FUNCTION_REGEX, line)

            if match_result:  # Inside a function's code
                counter = 0
                cur_function = match_result.group(1)
                result[cur_function] = {}
                continue

            match_result2 = re.search(CALLSITE_REGEX[arch], line)

            if match_result2:  # Found a call instruction

                nextLine = lines[index + 1]
                match_result3 = re.match(RETURN_ADDRESS_REGEX, nextLine)  # Parsing instruction after the call

                if not match_result3:
                    print('Unreachable')
                else:
                    cur_label = '.L' + cur_function + str(counter)
                    result[cur_function][cur_label] = match_result3.group(1)
                    counter = counter + 1

    return result


def align(text1, text2):
    """ Return the callsite padding as a lit for two different objdump outputs.

    Get a clean output of objdump by keeping only line of the .text section that have calls.
    Calculate the necessary padding for the architectures (currently x86-64 and ARM-v8 supported).
    For x86-64 call instructions should end at a 4-byte boundary. See: TODO

    https://stackoverflow.com/questions/67578127/align-x86-64-and-aarch64-callsites

    Aarch64 instructions should be 4-byte aligned.

    @param text1: objdump input for x86-64
    @param text2: objdump input for arm-v8
    @return:
    """
    d1 = get_return_addresses(text1, 'x86-64')
    d2 = get_return_addresses(text2, 'aarch64')

    padding_dict = {'x86-64': {}, 'aarch64': {}}
    for function in d1.keys():

        # Accumulated paddings for each function in both architectures
        total_padding1 = 0
        total_padding2 = 0

        for label in d1[function].keys():

            # Offsets of call instructions from the caller function's symbol
            offset1 = int(d1[function][label], 16) + total_padding1
            offset2 = int(d2[function][label], 16) + total_padding2

            diff = offset1 - offset2
            padding1 = 0
            padding2 = 0

            if diff < 0:
                padding1 = abs(diff)  # We assume that x86-64 can be padded arbitrarily...
                padding2 = 0

            if diff > 0:
                padding1 = diff % 4  # ...whereas we know that arm-v8 instructions must be 4-byte aligned
                if padding1 == 0:
                    padding2 = diff
                else:
                    padding2 = 4 * (diff // 4 + 1)

            padding_dict['x86-64'][label] = padding1
            padding_dict['aarch64'][label] = padding2
            total_padding1 = total_padding1 + padding1
            total_padding2 = total_padding2 + padding2

    print(json.dumps(padding_dict))


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print('Usage: ./callsite_align <objdump_input_x86> <objdump_input_arm>')
        sys.exit(1)

    align(sys.argv[1], sys.argv[2])
