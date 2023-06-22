# RUN: print_ascii_stack.py -i %s -f main -c 1 -a arm | filecheck %s

# CHECK:      0x0  : ||x29------|| : 0x0
# CHECK-NEXT: 0x8  : ||x30------|| : 0x8
# CHECK-NEXT:
# CHECK-NEXT: sp : 0x0

0000000000501040 main:
; {
  501040: ff 43 03 d1                  	sub	sp, sp, #0x10
  501048: fd 7b 0c a9                  	stp	x29, x30, [sp]
