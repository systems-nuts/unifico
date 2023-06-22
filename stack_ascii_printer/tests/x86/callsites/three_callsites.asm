# RUN: print_ascii_stack.py -i %s -f main -c 3 -a x86 | filecheck %s

# CHECK:      0x0  : ||---------|| : -0xc0
# CHECK-NEXT: 0x8  : ||----|eax-|| : -0xb8
# CHECK-NEXT: 0x10 : ||---------|| : -0xb0
# CHECK-NEXT: 0x18 : ||---------|| : -0xa8
# CHECK-NEXT: 0x20 : ||---------|| : -0xa0
# CHECK-NEXT: 0x28 : ||---------|| : -0x98
# CHECK-NEXT: 0x30 : ||---------|| : -0x90
# CHECK-NEXT: 0x38 : ||---------|| : -0x88
# CHECK-NEXT: 0x40 : ||---------|| : -0x80
# CHECK-NEXT: 0x48 : ||---------|| : -0x78
# CHECK-NEXT: 0x50 : ||---------|| : -0x70
# CHECK-NEXT: 0x58 : ||---------|| : -0x68
# CHECK-NEXT: 0x60 : ||---------|| : -0x60
# CHECK-NEXT: 0x68 : ||---------|| : -0x58
# CHECK-NEXT: 0x70 : ||---------|| : -0x50
# CHECK-NEXT: 0x78 : ||---------|| : -0x48
# CHECK-NEXT: 0x80 : ||---------|| : -0x40
# CHECK-NEXT: 0x88 : ||---------|| : -0x38
# CHECK-NEXT: 0x90 : ||xmm0-----|| : -0x30
# CHECK-NEXT: 0x98 : ||xmm0-----|| : -0x28
# CHECK-NEXT: 0xa0 : ||rsi------|| : -0x20
# CHECK-NEXT: 0xa8 : ||edi-|0x0-|| : -0x18
# CHECK-NEXT: 0xb0 : ||---------|| : -0x10
# CHECK-NEXT: 0xb8 : ||rbx------|| : -0x8
# CHECK-NEXT: 0xc0 : ||rbp------|| : 0x0
# CHECK-NEXT: 0xc8 : ||---------|| : 0x8
# CHECK-NEXT:
# CHECK-NEXT: rsp: 0x0
# CHECK-NEXT: rbp: 0xc0


0000000000501040 <main>:

int main(int argc, char **argv)
{
  501040:	55                   	push   rbp
  501041:	48 89 e5             	mov    rbp,rsp
  501044:	53                   	push   rbx
  501045:	48 81 ec b8 00 00 00 	sub    rsp,0xb8
  50104c:	c7 45 ec 00 00 00 00 	mov    DWORD PTR [rbp-0x14],0x0
  501053:	89 7d e8             	mov    DWORD PTR [rbp-0x18],edi
  501056:	48 89 75 e0          	mov    QWORD PTR [rbp-0x20],rsi
  50105a:	f2 0f 10 05 c6 10 10 	movsd  xmm0,QWORD PTR [rip+0x1010c6]        # 602128 <__log_data+0x1090>
  501061:	00 
  double d1, d2;
  double B[16];

  d1 = log(1.0);
  501062:	90                   	nop
  501063:	e8 0c 09 00 00       	call   501974 <log>
  501068:	f2 0f 11 45 d8       	movsd  QWORD PTR [rbp-0x28],xmm0
  50106d:	f2 0f 10 05 bb 10 10 	movsd  xmm0,QWORD PTR [rip+0x1010bb]        # 602130 <__log_data+0x1098>
  501074:	00 
  d2 = log(2.0);
  501075:	66 90                	xchg   ax,ax
  501077:	e8 f8 08 00 00       	call   501974 <log>
  50107c:	f2 0f 11 45 d0       	movsd  QWORD PTR [rbp-0x30],xmm0
  501081:	b8 01 00 00 00       	mov    eax,0x1
  for (int i = 1; i < 10; ++i) {
  501086:	89 85 4c ff ff ff    	mov    DWORD PTR [rbp-0xb4],eax
  50108c:	83 bd 4c ff ff ff 09 	cmp    DWORD PTR [rbp-0xb4],0x9
  501093:	0f 8f 22 00 00 00    	jg     5010bb <main+0x7b>
      simple(i);
  501099:	8b 9d 4c ff ff ff    	mov    ebx,DWORD PTR [rbp-0xb4]
  50109f:	89 df                	mov    edi,ebx
  5010a1:	66 90                	xchg   ax,ax
  5010a3:	e8 78 ff ff ff       	call   501020 <simple>
  for (int i = 1; i < 10; ++i) {
  5010a8:	ff 85 4c ff ff ff    	inc    DWORD PTR [rbp-0xb4]
  5010ae:	83 bd 4c ff ff ff 09 	cmp    DWORD PTR [rbp-0xb4],0x9
  5010b5:	0f 8e de ff ff ff    	jle    501099 <main+0x59>
  }

  return 0;
  5010bb:	31 c0                	xor    eax,eax
  5010bd:	48 81 c4 b8 00 00 00 	add    rsp,0xb8
  5010c4:	5b                   	pop    rbx
  5010c5:	5d                   	pop    rbp
  5010c6:	c3                   	ret    
	...
