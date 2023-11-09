from align.stack_slot_align import (
    get_stack_slots,
    check_stack_slot_number,
)


def compare_stack_slot_align(text1, text2):
    """Check that the callsites of two different objdump outputs are padded.

    Check that the stack slot alignment is the same for the architectures (currently x86-64
    and ARM-v8 supported).
    Otherwise, print the differences.

    @param text1: objdump input for aarch64
    @param text2: objdump input for x86-64
    @return: Return successfully or exit in the case of failure
    """
    d1 = get_stack_slots(text1)
    d2 = get_stack_slots(text2)

    check_stack_slot_number(d1, d2)

    if d1 == d2:
        return True

    for function in d1.keys():
        if d1[function] != d2[function]:
            for label in d1[function].keys():
                print(label, d1[function][label], "----", d2[function][label])

    return False
