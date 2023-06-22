# RUN: print_ascii_stack.py -i %s -f spill -c 2 -a x86 | filecheck %s

CHECK:      0x0  : ||---------|| : -0x20
CHECK-NEXT: 0x8  : ||---------|| : -0x18
CHECK-NEXT: 0x10 : ||----|xmm0|| : -0x10
CHECK-NEXT: 0x18 : ||---------|| : -0x8
CHECK-NEXT: 0x20 : ||rbp------|| : 0x0
CHECK-NEXT: 0x28 : ||---------|| : 0x8
# CHECK-NEXT:
# CHECK-NEXT: rsp: 0x0
# CHECK-NEXT: rbp: 0x20

0000000000501040 <spill>:
  501040:	55                   	push   rbp
  501041:	48 89 e5             	mov    rbp,rsp
  501044:	48 83 ec 20          	sub    rsp,0x20
  501048:	f3 0f 10 05 a0 0b 10 	movss  xmm0,DWORD PTR [rip+0x100ba0]        # 601bf0 <errmsg+0x720>
  50104f:	00
  501050:	0f 1f 00             	nop    DWORD PTR [rax]
  501053:	e8 c8 ff ff ff       	call   501020 <func>
  501058:	f3 0f 11 45 f4       	movss  DWORD PTR [rbp-0xc],xmm0
  501063:	e8 c8 ff ff ff       	call   501020 <func>
