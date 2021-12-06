import pytest

from layout.callsites.callsite_align import *
from layout.callsites.check_callsite_align import check_callsite_align

# TODO: add test for get_return_addresses


def test_align():
    """
    Test whether the function properly aligns the callsites given two objdump files,
    by returning the correct padding dictionary.
    """
    input1 = 'layout/callsites/test/pass/objdump-arm.txt'
    input2 = 'layout/callsites/test/pass/objdump-x86.txt'

    padding_dict = align(input1, input2)

    target_dict = {
        'aarch64': {
            '.Lmain0': 12,
            '.Lmain1': 0
        },
        'x86-64': {
            '.Lmain0': 2,
            '.Lmain1': 1
        }
    }

    assert padding_dict == target_dict


def test_different_callsite_number_pass():
    """
    Test whether the function properly detects different number of callsites in the objdump files.
    """
    input1 = get_return_addresses('layout/callsites/test/pass/objdump-arm.txt', 'aarch64')
    input2 = get_return_addresses('layout/callsites/test/pass/objdump-x86.txt', 'x86-64')

    check_callsite_number(input1, input2)


def test_different_callsite_number_fail():
    """
    Test whether the function properly detects different number of callsites in the objdump files.
    """
    input1 = get_return_addresses('layout/callsites/test/fail/objdump-arm.txt', 'aarch64')
    input2 = get_return_addresses('layout/callsites/test/fail/objdump-x86.txt', 'x86-64')

    print()
    with pytest.raises(SystemExit) as e:
        check_callsite_number(input1, input2)
    assert e.type == SystemExit
    assert e.value.code == 1


def test_check_callsite_align_pass():
    """
    Test whether the function properly checks that the callsites of the two objdump files are properly aligned.
    """
    input1 = 'layout/callsites/test/pass/aligned-objdump-arm.txt'
    input2 = 'layout/callsites/test/pass/aligned-objdump-x86.txt'

    check_callsite_align(input1, input2)


def test_check_callsite_align_fails():
    """
    Test whether the function properly checks that the callsites of the two objdump files are not properly aligned.
    """
    input1 = 'layout/callsites/test/pass/objdump-arm.txt'
    input2 = 'layout/callsites/test/pass/objdump-x86.txt'

    print()
    with pytest.raises(SystemExit) as e:
        check_callsite_align(input1, input2)
    assert e.type == SystemExit
    assert e.value.code == 1
