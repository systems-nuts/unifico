from layout.callsites.callsite_align import *

# TODO: add test for get_return_addresses


def test_align():
    """
    Test whether the function properly aligns the callsites given two objdump files.
    """
    input1 = 'layout/callsites/test/objdump-arm.txt'
    input2 = 'layout/callsites/test/objdump-x86.txt'

    padding_dict = align(input1, input2)

    target_dict = {
        'aarch64': {
            '.Lmain0': 12,
            '.Lmain1': 0
        },
        'x86-64': {
            '.Lmain0': 2,
            '.Lmain1': 1
        },
    }

    assert padding_dict == target_dict
