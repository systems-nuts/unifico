# RUN: print_ascii_stack.py -i %s -f main -c 1 | filecheck %s

# CHECK:      0x0   : ||----|w19|--------|| : 0x0
# CHECK-NEXT:
# CHECK-NEXT: sp : 0x0

0000000000501040 main:
; {
  501040: ff 43 03 d1                  	sub	sp, sp, #0x10
  501044: f3 5f 00 f9                  	str	w19, [sp, #0x4]
