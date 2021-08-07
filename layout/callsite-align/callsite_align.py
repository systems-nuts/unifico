import re


FUNCTION_REGEX = '0+\s<(\w+)>:.*'
X86_64_CALLSITE_REGEX = '\w\w:.*callq.*'
ARM_V8_CALLSITE_REGEX = '\w\w:.*bl.*'
RETURN_ADDRESS_REGEX = '(\w\w):.*'


def get_return_addresses(objdump_output):
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
    @return: dictionary
    """
    with open(objdump_output, "r") as objdump_file:
        lines = objdump_file.readlines()
        for index, line in enumerate(lines):
            s = None
            matchResult = re.match(FUNCTION_REGEX, line)
            if matchResult:  # Inside a function's code
                nextLine = lines[index + 1]
                matchResult2 = re.match(twoLinesRe2, nextLine)
                if matchResult2:
                    name = matchResult.group(1)
                    address = int(matchResult2.group(1), 0)
                    size = int(matchResult2.group(2), 0)
                    alignment = int(matchResult2.group(3), 0)
                    objectFile = matchResult2.group(4)
                    s = Symbol.Symbol(name, address, size, alignment,
                                      objectFile, self.getArch())
                else:
                    er("missed a two lines symbol while parsing    objdump_file:\n")
                    er("line1: " + line + "\n")
                    er("line2: " + nextLine + "\n")
                    sys.exit(-1)
            else:
                matchResult3 = re.match(oneLineRe, line)
                if matchResult3:  # one line symbol description
                    name = matchResult3.group(1)
                    address = int(matchResult3.group(2), 0)
                    size = int(matchResult3.group(3), 0)
                    alignment = int(matchResult3.group(4), 0)
                    objectFile = matchResult3.group(5)

                    if name == '.text':
                        nextLine = lines[index + 1]
                        matchResult4 = re.match(extraLineRe, nextLine)
                        our_symbols = ['__set_thread_area', 'memcpy', 'memset']
                        our_symbols = ['__set_thread_area']
                        if matchResult4 and matchResult4.group(2) in our_symbols:
                            name = name + '.' + matchResult4.group(2)
                            print(name)
                    s = Symbol.Symbol(name, address, size, alignment,
                                      objectFile, self.getArch())

            if s:
                res.append(s)

    return res


def align(text1, text2):
    """ Return the callsite padding as a lit for two different objdump outputs.

    Get a clean output of objdump by keeping only line of the .text section that have calls.
    Calculate the necessary padding for the architectures (currently x86-64 and ARM-v8 supported).
    For x86-64 call instructions should end at a 4-byte boundary. See: TODO

    https://stackoverflow.com/questions/67578127/align-x86-64-and-aarch64-callsites

    Aarch64 instructions should be 4-byte aligned.

    @param text1:
    @param text2:
    @return:
    """
