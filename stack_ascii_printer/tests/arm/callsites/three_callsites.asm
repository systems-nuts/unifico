# RUN: print_ascii_stack.py -i %s -f main -c 3 -a arm | filecheck %s

# CHECK:      0x0  : ||---------|| : -0xc0
# CHECK-NEXT: 0x8  : ||----|w8--|| : -0xb8
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
# CHECK-NEXT: 0x90 : ||d0-------|| : -0x30
# CHECK-NEXT: 0x98 : ||d0-------|| : -0x28
# CHECK-NEXT: 0xa0 : ||x2-------|| : -0x20
# CHECK-NEXT: 0xa8 : ||w0--|wzr-|| : -0x18
# CHECK-NEXT: 0xb0 : ||x19------|| : -0x10
# CHECK-NEXT: 0xb8 : ||---------|| : -0x8
# CHECK-NEXT: 0xc0 : ||x29------|| : 0x0
# CHECK-NEXT: 0xc8 : ||x30------|| : 0x8
# CHECK-NEXT: 0xd0 : ||w0--|wzr-|| : 0x10
# CHECK-NEXT:
# CHECK-NEXT: sp : 0x0
# CHECK-NEXT: x29: 0xc0
# CHECK-NEXT: x19: 0x90


0000000000501040 main:
; {
  501040: ff 43 03 d1                  	sub	sp, sp, #0xd0
  501044: f3 5f 00 f9                  	str	x19, [sp, #0xb0]
  501048: fd 7b 0c a9                  	stp	x29, x30, [sp, #0xc0]
  50104c: fd 03 03 91                  	add	x29, sp, #0xc0
  501050: 08 08 00 b0                  	adrp	x8, #0x101000
  501054: 00 95 40 fd                  	ldr	d0, [x8, #0x128]
  501058: b3 c3 00 d1                  	sub	x19, x29, #0x30
  50105c: a0 7f 3d 29                  	stp	w0, wzr, [x29, #-0x18]
  50105c: a0 7f 3d 29                  	stp	w0, wzr, [x29, #0x10]
  501060: 61 0a 00 f9                  	str	x1, [x19, #0x10]
  501060: 61 0a 00 f9                  	str	x2, [x19, #0x10]
;   d1 = log(1.0);
  501064: 44 02 00 94                  	bl	#0x910 <log>
  501068: 08 08 00 b0                  	adrp	x8, #0x101000
  50106c: 60 06 00 fd                  	str	d0, [x19, #0x8]
  501070: 00 99 40 fd                  	ldr	d0, [x8, #0x130]
;   d2 = log(2.0);
  501074: 1f 20 03 d5                  	nop
  501078: 3f 02 00 94                  	bl	#0x8fc <log>
  50107c: 28 00 80 52                  	mov	w8, #0x1
  501080: 60 02 00 fd                  	str	d0, [x19]
  501084: e8 0f 00 b9                  	str	w8, [sp, #0xc]
;   for (int i = 1; i < 10; ++i) {
  501088: e8 03 08 2a                  	mov	w8, w8
  50108c: 1f 25 00 71                  	cmp	w8, #0x9
  501090: 2c 01 00 54                  	b.gt	#0x24 <main+0x74>
;       simple(i);
  501094: f3 0f 40 b9                  	ldr	w19, [sp, #0xc]
  501098: e0 03 13 2a                  	mov	w0, w19
  50109c: 1f 20 03 d5                  	nop
  5010a0: 1f 20 03 d5                  	nop
  5010a4: df ff ff 97                  	bl	#-0x84 <simple>
;   for (int i = 1; i < 10; ++i) {
  5010a8: e8 0f 40 b9                  	ldr	w8, [sp, #0xc]
  5010ac: 08 05 00 11                  	add	w8, w8, #0x1
  5010b0: f5 ff ff 17                  	b	#-0x2c <main+0x44>
;   return 0;
  5010b4: fd 7b 4c a9                  	ldp	x29, x30, [sp, #0xc0]
  5010b8: f3 5f 40 f9                  	ldr	x19, [sp, #0xb8]
  5010bc: e8 03 1f 2a                  	mov	w8, wzr
  5010c0: ff 43 03 91                  	add	sp, sp, #0xd0
  5010c4: c0 03 5f d6                  	ret

00000000005010c8 _start_c:
; {
  5010c8: ff 43 02 d1                  	sub	sp, sp, #0x90
  5010cc: f4 4f 07 a9                  	stp	x20, x19, [sp, #0x70]
  5010d0: fd 7b 08 a9                  	stp	x29, x30, [sp, #0x80]
; 	register int argc = p[0];
  5010d4: e6 03 00 aa                  	mov	x6, x0
