import sys

from callsite_align import get_return_addresses


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print('Usage: ./test_callsite_align <objdump_input_x86> <objdump_input_arm>')
        sys.exit(1)

    ret_code = 0

    d1 = get_return_addresses(sys.argv[1], 'x86-64')
    d2 = get_return_addresses(sys.argv[2], 'aarch64')

    if d1 != d2:
        ret_code = 1  # If callsites are not aligned return with 1 error status

    sys.exit(ret_code)
