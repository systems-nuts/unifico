# RUN: print_ascii_stack.py -i %s -f main -c 1 -a x86 | filecheck %s

# CHECK:      0x0  : ||r19------|| : -0x10
# CHECK-NEXT: 0x8  : ||rbx------|| : -0x8
# CHECK-NEXT: 0x10 : ||rbp------|| : 0x0
# CHECK-NEXT: 0x18 : ||---------|| : 0x8
# CHECK-NEXT:
# CHECK-NEXT: rsp: 0x0
# CHECK-NEXT: rbp: 0x10

0000000000501050 <main>:
  501050:	55                   	push   rbp
  501051:	48 89 e5             	mov    rbp,rsp
  501054:	53                   	push   rbx
  501054:	53                   	push   r19
