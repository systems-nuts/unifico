import pytest

from layout.slots.align.stack_slot_align import (
    align_stack_slots,
    get_stack_slots,
    check_stack_slot_number,
)
from layout.slots.align.compare import compare_stack_slot_align

TEST_INPUT_PATH = "input/"


def test_align_stack_slots():
    """
    Test whether the function properly aligns the stack slots given two stack slot
    files by returning the correct padding dictionary.
    """
    input1 = TEST_INPUT_PATH + "pass/arm.txt"
    input2 = TEST_INPUT_PATH + "pass/x86.txt"

    padding_dict = align_stack_slots(input1, input2)

    target_dict = {
        "results": {"0": 16},
        "main": {"0": 8},
    }

    assert padding_dict == target_dict


def test_different_function_number_fail():
    """
    Test whether the function properly detects different number of functions.
    """
    input1 = get_stack_slots(TEST_INPUT_PATH + "fail/1-func-arm.txt")
    input2 = get_stack_slots(TEST_INPUT_PATH + "fail/2-func-x86.txt")

    print()
    with pytest.raises(SystemExit) as e:
        check_stack_slot_number(input1, input2)
    assert e.type == SystemExit
    assert e.value.code == 1


def test_different_stack_slot_number_pass():
    """
    Test whether the function properly detects different number of stack slots.
    """
    input1 = get_stack_slots(TEST_INPUT_PATH + "pass/arm.txt")
    input2 = get_stack_slots(TEST_INPUT_PATH + "pass/x86.txt")

    assert check_stack_slot_number(input1, input2)


def test_different_stack_slot_number_fail():
    """
    Test whether the function properly detects different number of stack slots.
    """
    input1 = get_stack_slots(TEST_INPUT_PATH + "fail/arm.txt")
    input2 = get_stack_slots(TEST_INPUT_PATH + "fail/x86.txt")

    print()
    assert not check_stack_slot_number(input1, input2)


def test_compare_stack_slot_align_pass():
    """
    Test whether the function properly checks that the stack slots of the two
    stack slot files are properly aligned.
    """
    input1 = TEST_INPUT_PATH + "pass/aligned-arm.txt"
    input2 = TEST_INPUT_PATH + "pass/aligned-x86.txt"

    assert compare_stack_slot_align(input1, input2)


def test_compare_stack_slot_align_fails():
    """
    Test whether the function properly checks that the stack slots of the two
    stack slot files are not properly aligned.
    """
    input1 = TEST_INPUT_PATH + "pass/arm.txt"
    input2 = TEST_INPUT_PATH + "pass/x86.txt"

    print()
    assert not compare_stack_slot_align(input1, input2)
