# RUN: print_ascii_stack.py -i %s -f main -c 1 -a x86 | filecheck %s

# CHECK:      0x0  : ||rbp------|| : 0x0
# CHECK-NEXT: 0x8  : ||---------|| : 0x8
# CHECK-NEXT: 0x10 : ||edi------|| : 0x10
# CHECK-NEXT:
# CHECK-NEXT: rsp: 0x0
# CHECK-NEXT: rbp: 0x0

0000000000501040 main:
; {
  501050:	55                   	push   rbp
  501041:	48 89 e5             	mov    rbp,rsp
  501053:	89 7d e8             	mov    DWORD PTR [rbp+0x10],edi
