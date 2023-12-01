#!/usr/bin/env python3

import re
import sys
import argparse

FRAME_LINE = "||---------||"


FUNCTION_REGEX = re.compile(
    r"""
 [0-9a-fA-F]+   # Function symbol address
 \s         # A whitespace
 <?(\w+)>?: # Function name, optionally enclosed in '<...>'
 .*         # Ignore rest
""",
    re.VERBOSE,
)

ARM_FRAME_SETUP = re.compile(
    r"""
 \s+                # Whitespaces
 [0-9a-fA-F]+:      # Instruction address
 [0-9a-fA-F\s]+     # Instruction encoding in hex form including whitespaces
 sub \s sp, \s sp, \s \#  # Frame setup instruction
 (0x[0-9a-fA-F]+)   # Frame size
 .*                 # Ignore rest
""",
    re.VERBOSE,
)

ARM_CREATE_PTR = re.compile(
    r"""
 \s+                # A whitespace
 [0-9a-fA-F]+:      # Instruction address
 [0-9a-fA-F\s]+     # Instruction encoding in hex form including whitespaces
 (add|sub) \s (\w+),\s (\w+), \s \#  # Pointer creation instruction
 (0x[0-9a-fA-F]+)   # Offset from stack pointer or frame pointer
 .*                 # Ignore rest
""",
    re.VERBOSE,
)

ARM_STR = re.compile(
    r"""
 \s+                # A whitespace
 [0-9a-fA-F]+:      # Instruction address
 [0-9a-fA-F\s]+     # Instruction encoding in hex form including whitespaces
 stu?r \s (\w+),\s \[(\w+)    # `str` instruction
 (, \s \#(-)?(0x[0-9a-fA-F]+))?]   # Offset from the definining pointer
 .*                 # Ignore rest
""",
    re.VERBOSE,
)

ARM_STP = re.compile(
    r"""
 \s+                # A whitespace
 [0-9a-fA-F]+:      # Instruction address
 [0-9a-fA-F\s]+     # Instruction encoding in hex form including whitespaces
 stp \s (\w+), \s (\w+), \s \[(\w+)     # `stp` instruction
 (, \s \#(-)?(0x[0-9a-fA-F]+))?]   # Offset from stack pointer or frame pointer
 .*                 # Ignore rest
""",
    re.VERBOSE,
)

ARM_CALLSITE = re.compile(
    r"""
 \s+                # Whitespaces
 [0-9a-fA-F]+:      # Instruction address
 [0-9a-fA-F\s]+     # Instruction encoding in hex form including whitespaces
 bl \s+ \# -? 0x[0-9a-fA-F]+ \s+ <(\w+)> # Frame setup instruction
 .*                 # Ignore rest
""",
    re.VERBOSE,
)

X86_PUSH = re.compile(
    r"""
 \s+                # Whitespaces
 [0-9a-fA-F]+:      # Instruction address
 [0-9a-fA-F\s]+     # Instruction encoding in hex form including whitespaces
 push \s+ (\w+)      # Frame setup instruction
 .*                 # Ignore rest
""",
    re.VERBOSE,
)

X86_FRAME_SETUP = re.compile(
    r"""
 \s+                # Whitespaces
 [0-9a-fA-F]+:      # Instruction address
 [0-9a-fA-F\s]+     # Instruction encoding in hex form including whitespaces
 sub \s+ rsp,       # Frame setup instruction
 (0x[0-9a-fA-F]+)   # Frame size
 .*                 # Ignore rest
""",
    re.VERBOSE,
)

X86_CREATE_PTR = re.compile(
    r"""
 \s+                # A whitespace
 [0-9a-fA-F]+:      # Instruction address
 [0-9a-fA-F\s]+     # Instruction encoding in hex form including whitespaces
 mov \s+ rbp,rsp    # Pointer creation instruction
 .*                 # Ignore rest
""",
    re.VERBOSE,
)

X86_MOV_XWORD = re.compile(
    r"""
 \s+                # A whitespace
 [0-9a-fA-F]+:      # Instruction address
 [0-9a-fA-F\s]+     # Instruction encoding in hex form including whitespaces
 mov\w* \s+ ([DQ]|XMM)WORD \s PTR \s \[(rsp|rbp)    # `mov` instruction
 (([+-])(0x[0-9a-fA-F]+))?]   # Offset from stack pointer or frame pointer
 ,([\d\w]+)           # Value to store
 .*                 # Ignore rest
""",
    re.VERBOSE,
)

X86_CALLSITE = re.compile(
    r"""
 \s+                # Whitespaces
 [0-9a-fA-F]+:      # Instruction address
 [0-9a-fA-F\s]+     # Instruction encoding in hex form including whitespaces
 call \s+ [0-9a-fA-F]+ \s+ <(\w+)> # Frame setup instruction
 .*                 # Ignore rest
""",
    re.VERBOSE,
)


class ProgramState:
    """
    Represents the execution state of the program.

    Attributes
    ----------
    stack: List(str)
        A list of strings where each string represents a quad-word sized frame line.
    registers: Dict
        Registers used for accessing objects in the stack, mapped to their offset from the stack pointer.
        Must have been initialized with an offset from the stack or frame pointer.
        e.g., {'sp': 0, 'fp': 16}, assuming that fp = sp + 16.
    frame_lines: int
        The number of quad words contained in the stack frame.
        Does not include quad words from the previous frame, e.g., arguments passed by the callee.
    callsites: int
        The number of callsites seen so far.
    """

    def __init__(self, arch):
        """
        Create a new program state.
        """
        self.stack = [FRAME_LINE] if arch == "x86" else []
        self.registers = {}
        self.frame_lines = 0
        self.callsites = 0
        self.stack_pointer = "rsp" if arch == "x86" else "sp"
        self.frame_pointer = "rbp" if arch == "x86" else "x29"

    def print_stack(self):
        sp_offset = self.registers.get(self.stack_pointer, 0)
        fp_offset = sp_offset - self.registers.get(self.frame_pointer, 0)
        frame_slots = self.stack
        while frame_slots:
            print(f"{hex(sp_offset):5s}: ", end="")
            print(frame_slots.pop(), end="")
            print(f" : {hex(fp_offset):6s}")
            sp_offset += 8
            fp_offset += 8

    def print_registers(self):
        for k, v in self.registers.items():
            print(f"{k:3s}: {hex(v)}")

    def print_state(self):
        self.print_stack()
        print()
        self.print_registers()

    def push(self, reg, offset):
        """
        Record the insertion of `reg` into the stack.

        Replaces the ASCII art representing the frame line with the `reg` name at `offset` from the stack pointer.
        If the push happens for a line of the previous frame, add the extra lines of the previous frame to the current.
        These lines are not counted in the `frame_lines` attribute of the class.
        @param reg: str
        @param offset: int
        @return:
        """
        if self.frame_lines <= 0:
            sys.exit("Cannot place register in an empty stack!")

        target_frame_index = len(self.stack) - abs(offset) // 8 - 1
        slack = -target_frame_index
        while slack > 0:
            self.stack.insert(0, FRAME_LINE)
            slack -= 1
            target_frame_index += 1

        target_ascii_line = self.stack[target_frame_index]
        target_word = offset % 8

        if target_word == 0:
            target_ascii_line = re.sub(
                len(reg) * r"[\w-]", reg, target_ascii_line, count=1
            )
        elif target_word == 4:
            target_ascii_line = (
                target_ascii_line[:6] + "|" + target_ascii_line[7:]
            )
            target_ascii_line = target_ascii_line[0:7] + re.sub(
                len(reg) * r"[\w-]", reg, target_ascii_line[7:], count=1
            )

        self.stack[target_frame_index] = target_ascii_line


def parse_arm_asm(input_file, func_name="main", callsite=1):
    program_state = ProgramState("arm")

    with open(input_file, "r") as objdump_file:
        lines = objdump_file.readlines()

        current_func = ""
        found_function = False

        for line in lines:
            # Parse function
            match_result = FUNCTION_REGEX.match(line)
            if match_result:
                current_func = match_result.group(1)
                if current_func == func_name:
                    found_function = True
            if found_function and current_func != func_name:
                break
            if current_func != func_name:
                continue

            # Parse frame setup instruction
            match_result = ARM_FRAME_SETUP.match(line)
            if match_result:
                frame_size = int(match_result.group(1), 16)
                if frame_size % 16 != 0:
                    sys.exit("Frame size not quad-word aligned!")
                quad_words = frame_size // 8
                program_state.stack.extend(quad_words * [FRAME_LINE])
                program_state.frame_lines += quad_words
                program_state.registers["sp"] = 0
                continue

            # Parse additions/subtractions from pointers
            match_result = ARM_CREATE_PTR.match(line)
            if match_result:
                operator = match_result.group(1)
                first_operand = match_result.group(2)
                second_operand = match_result.group(3)
                offset = int(match_result.group(4), 16)
                if second_operand in program_state.registers.keys():
                    if operator == "sub":
                        offset = -offset
                    program_state.registers[first_operand] = (
                        program_state.registers[second_operand] + offset
                    )
                continue

            # Parse `str` instructions
            match_result = ARM_STR.match(line)
            if match_result:
                first_operand = match_result.group(1)
                second_operand = match_result.group(2)
                offset_string = match_result.group(3)
                if offset_string:
                    sign = match_result.group(4)
                    offset = int(match_result.group(5), 16)
                    offset = -offset if sign else offset
                else:
                    offset = 0
                if second_operand not in program_state.registers.keys():
                    print(
                        f"WARNING: Storing using an untracked pointer:\n{line}",
                        file=sys.stderr,
                    )
                    continue
                offset = program_state.registers[second_operand] + offset
                program_state.push(first_operand, offset)
                continue

            # Parse `stp` instructions
            match_result = ARM_STP.match(line)
            if match_result:
                first_operand = match_result.group(1)
                second_operand = match_result.group(2)
                third_operand = match_result.group(3)
                offset_string = match_result.group(4)
                if offset_string:
                    sign = match_result.group(5)
                    offset = int(match_result.group(6), 16)
                    offset = -offset if sign else offset
                else:
                    offset = 0
                if third_operand not in program_state.registers.keys():
                    print(
                        f"WARNING: Storing using an untracked pointer:\n{line}",
                        file=sys.stderr,
                    )
                    continue
                offset = program_state.registers[third_operand] + offset
                program_state.push(first_operand, offset)
                additional_offset = 8 if first_operand[0] == "x" else 4
                program_state.push(second_operand, offset + additional_offset)
                continue

            # Parse callsite
            match_result = ARM_CALLSITE.match(line)
            if match_result:
                program_state.callsites += 1
                if program_state.callsites == callsite:
                    break
                continue

        program_state.print_state()


def parse_x86_asm(input_file, func_name="main", callsite=1):
    program_state = ProgramState("x86")

    with open(input_file, "r") as objdump_file:
        lines = objdump_file.readlines()

        current_func = ""
        found_function = False

        for line in lines:
            # Parse function
            match_result = FUNCTION_REGEX.match(line)
            if match_result:
                current_func = match_result.group(1)
                if current_func == func_name:
                    found_function = True
            if found_function and current_func != func_name:
                break
            if current_func != func_name:
                continue

            # Parse `push` instruction
            match_result = X86_PUSH.match(line)
            if match_result:
                register = match_result.group(1)
                if len(program_state.stack) == 1:
                    program_state.registers["rsp"] = 0
                if "rbp" in program_state.registers.keys():
                    program_state.registers["rbp"] += 8
                program_state.stack.extend([FRAME_LINE])
                program_state.frame_lines += 1
                program_state.push(register, 0)
                # Check if we set up the frame for the first time
                continue

            # Parse `mov rbp,rsp`
            match_result = X86_CREATE_PTR.match(line)
            if match_result:
                program_state.registers["rbp"] = program_state.registers["rsp"]
                continue

            # Parse frame setup instruction
            match_result = X86_FRAME_SETUP.match(line)
            if match_result:
                frame_size = int(match_result.group(1), 16)
                quad_words = frame_size // 8
                program_state.stack.extend(quad_words * [FRAME_LINE])
                program_state.frame_lines += quad_words
                program_state.registers["rsp"] = 0
                for reg in program_state.registers.keys():
                    if reg != "rsp":
                        program_state.registers[reg] += quad_words * 8
                continue

            # Parse `mov DWORD PTR` instructions
            match_result = X86_MOV_XWORD.match(line)
            if match_result:
                pointer_register = match_result.group(2)
                offset = match_result.group(3)
                if offset:
                    sign = match_result.group(4)
                    offset = int(match_result.group(5), 16)
                    offset = -offset if sign == "-" else offset
                else:
                    offset = 0
                value = match_result.group(6)
                if pointer_register not in program_state.registers.keys():
                    print(
                        f"WARNING: Storing using an untracked pointer:\n{line}",
                        file=sys.stderr,
                    )
                    continue
                offset = program_state.registers[pointer_register] + offset
                program_state.push(value, offset)
                continue

            # Parse callsite
            match_result = X86_CALLSITE.match(line)
            if match_result:
                program_state.callsites += 1
                if program_state.callsites == callsite:
                    break
                continue

        program_state.print_state()


arg_parser = argparse.ArgumentParser(
    description="An ASCII art printer for the stack of x86 or arm executables."
)

arg_parser.add_argument(
    "-i", "--input_file", type=str, nargs="?", help="Path to input file"
)

arg_parser.add_argument(
    "-o", "--output_file", type=str, nargs="?", help="Path to output file"
)

arg_parser.add_argument(
    "-f", "--function", type=str, nargs="?", help="Function to examine"
)

arg_parser.add_argument(
    "-c",
    "--callsite",
    type=int,
    nargs="?",
    help="Up to which callsite to print (inclusive)",
)

arg_parser.add_argument(
    "-a",
    "--architecture",
    type=str,
    action="store",
    nargs="?",
    choices=["arm", "x86"],
    default="x86",
    help="Architecture to examine (default x86)",
)


def __main__():
    args = arg_parser.parse_args()

    if args.architecture == "arm":
        parse_arm_asm(args.input_file, args.function, args.callsite)
    elif args.architecture == "x86":
        parse_x86_asm(args.input_file, args.function, args.callsite)


if __name__ == "__main__":
    __main__()
