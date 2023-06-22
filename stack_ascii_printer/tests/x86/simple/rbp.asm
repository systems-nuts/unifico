# RUN: print_ascii_stack.py -i %s -f main -c 1 -a x86 | filecheck %s

# CHECK:      0x0 : ||rbp------|| : 0x0
# CHECK-NEXT: 0x8 : ||---------|| : 0x8
# CHECK-NEXT:
# CHECK-NEXT: rsp: 0x0

0000000000501050 <main>:
  501050:	55                   	push   rbp
