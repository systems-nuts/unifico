# RUN: print_ascii_stack.py -i %s -f main -c 1 -a x86 | filecheck %s

# CHECK:      0x0   : ||rsi-|esi-|| : -0x10
# CHECK-NEXT: 0x8   : ||rsi-|esi-|| : -0x8
# CHECK-NEXT: 0x10  : ||rbp------|| : 0x0
# CHECK-NEXT: 0x18  : ||---------|| : 0x8
# CHECK-NEXT:
# CHECK-NEXT: rsp: 0x0
# CHECK-NEXT: rbp: 0x10

0000000000501040 main:
  501020:	55                   	push   rbp
  501041:	48 89 e5             	mov    rbp,rsp
  501057:	48 81 ec 90 00 00 00 	sub    rsp,0x10

  501068:	48 89 75 d8          	mov    DWORD PTR [rsp],rdi
  501068:	48 89 75 d8          	mov    DWORD PTR [rsp],rsi

  501068:	48 89 75 d8          	mov    DWORD PTR [rsp+0x4],edi
  501068:	48 89 75 d8          	mov    DWORD PTR [rsp+0x4],esi

  501068:	48 89 75 d8          	mov    DWORD PTR [rsp+0x8],rdi
  501068:	48 89 75 d8          	mov    DWORD PTR [rsp+0x8],rsi

  501068:	48 89 75 d8          	mov    DWORD PTR [rsp+0xc],edi
  501068:	48 89 75 d8          	mov    DWORD PTR [rsp+0xc],esi
