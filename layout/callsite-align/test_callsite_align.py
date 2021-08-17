import sys
import re

# This verbose and more readable regex form, requires the re.VERBOSE flag in re.compile
FUNCTION_REGEX = re.compile(r"""
 \d+        # Function symbol address
 \s         # A whitespace
 <?(\w+)>?: # Function name, optionally enclosed in '<...>'
 .*         # Ignore rest
""", re.VERBOSE)

# Will be used with re.search
CALLSITE_REGEX = {
    'x86-64': r'\s(callq)\s',
    'aarch64': r'\s(bl)\s'
}

RETURN_ADDRESS_REGEX = re.compile(r"""
 \s*                # Initial whitespaces
 ([0-9a-fA-F]+):    # Hex offset
 .*                 # Ignore rest
""", re.VERBOSE)


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

            match_result = FUNCTION_REGEX.match(line)

            if match_result:  # Inside a function's code
                counter = 0
                cur_function = match_result.group(1)
                result[cur_function] = {}
                continue

            match_result2 = re.search(CALLSITE_REGEX[arch], line)

            if match_result2:  # Found a call instruction

                nextLine = lines[index + 1]
                match_result3 = RETURN_ADDRESS_REGEX.match(nextLine)  # Parsing instruction after the call

                if not match_result3:
                    print('Unreachable')
                else:
                    cur_label = '.L' + cur_function + str(counter)
                    result[cur_function][cur_label] = match_result3.group(1)
                    counter = counter + 1

    return result


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print('Usage: ./test_callsite_align <objdump_input_x86> <objdump_input_arm>')
        sys.exit(1)

    ret_code = 0

    d1 = get_return_addresses(sys.argv[1], 'x86-64')
    d2 = get_return_addresses(sys.argv[2], 'aarch64')

    for function in d1.keys():
        for label in d1[function].keys():
            print(label, d1[function][label], '----', d2[function][label])

    if d1 != d2:
        ret_code = 1  # If callsites are not aligned return with 1 error status

    sys.exit(ret_code)
