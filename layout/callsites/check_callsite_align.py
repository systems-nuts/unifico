import sys

from layout.callsites.callsite_align import get_return_addresses


def check_callsite_align(text1, text2):
    """ Check that the callsites of two different objdump outputs are padded.

    Get a clean output of objdump by keeping only line of the .text section that have calls.
    Check that the padding is the same for the architectures (currently x86-64 and ARM-v8 supported).
    Otherwise, print the differences.

    @param text1: objdump input for arm-v8
    @param text2: objdump input for x86-64
    @return: Return successfully or exit in the case of failure
    """
    d1 = get_return_addresses(text1, 'aarch64')
    d2 = get_return_addresses(text2, 'x86-64')

    if d1 == d2:
        return

    for function in d1.keys():
        if d1[function] != d2[function]:
            for label in d1[function].keys():
                print(label, d1[function][label], '----', d2[function][label])

    sys.exit(1)


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print('Usage: ./check_callsite_align<objdump_input_arm> <objdump_input_x86>')
        sys.exit(1)
    check_callsite_align(sys.argv[1], sys.argv[2])