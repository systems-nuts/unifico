 [IR] call_leaf.ll
~/llvm_9/toolchain/bin/clang -Xclang -disable-O0-optnone  -O0 -Wall -nostdinc -fno-common -ftls-model=initial-exec  -g -S -emit-llvm -isystem ~/musl-cross-make/output/aarch64-linux-musl/include -o call_leaf.ll call_leaf.c
Here!
# Remove the x86-64-related information
sed -e "s/\"target-cpu\"\=\"x86-64\"\ \"target-features\"\=\"+cx8,+fxsr,+mmx,+sse,+sse2,+x87\"//g" -i.backup call_leaf.ll
# Make directories
mkdir -p build_x86-64 build_aarch64
 [OPT] call_leaf_opt.ll
~/llvm_9/toolchain/bin/opt -name-string-literals -static-var-sections -S -o call_leaf_opt.ll call_leaf.ll
 [LLC] call_leaf_aarch64.o
~/llvm_9/toolchain/bin/llc -function-sections -data-sections  -march=aarch64 -filetype=obj -o call_leaf_aarch64.o call_leaf_opt.ll
 [LD] call_leaf_aarch64_unaligned.out
/usr/local/popcorn/bin/x86_64-popcorn-linux-gnu-ld.gold -o call_leaf_aarch64_unaligned.out call_leaf_aarch64.o -z noexecstack -z relro --hash-style=gnu --build-id -static -m aarch64linux -L~/musl-cross-make/output/aarch64-linux-musl/lib -L/usr/lib/gcc-cross/aarch64-linux-gnu/8 ~/musl-cross-make/output/aarch64-linux-musl/lib/crt1.o ~/musl-cross-make/output/aarch64-linux-musl/lib/libc.a ~/musl-cross-make/output/aarch64-linux-musl/lib/libm.a --start-group -lgcc -lgcc_eh --end-group -Map build_aarch64/map.txt
 [LLC] call_leaf_x86_64.o
~/llvm_9/toolchain/bin/llc -function-sections -data-sections  -march=x86-64 -filetype=obj -o call_leaf_x86_64.o call_leaf_opt.ll
 [LD] call_leaf_x86_64_unaligned.out
/usr/local/popcorn/bin/x86_64-popcorn-linux-gnu-ld.gold -o call_leaf_x86_64_unaligned.out call_leaf_x86_64.o -z noexecstack -z relro --hash-style=gnu --build-id -static -m elf_x86_64 -L~/musl-cross-make/output/x86_64-linux-musl/lib ~/musl-cross-make/output/x86_64-linux-musl/lib/crt1.o ~/musl-cross-make/output/x86_64-linux-musl/lib/libc.a ~/musl-cross-make/output/x86_64-linux-musl/lib/libm.a --start-group --end-group -Map build_x86-64/map.txt
 [ALIGN] build_x86-64/aligned_linker_script_x86.x
/usr/local/popcorn/bin/pyalign --compiler-inst /usr/local/popcorn \
	--x86-bin call_leaf_x86_64_unaligned.out --arm-bin call_leaf_aarch64_unaligned.out \
	--x86-map build_x86-64/map.txt --arm-map build_aarch64/map.txt \
	--output-x86-ls build_x86-64/aligned_linker_script_x86.x --output-arm-ls build_aarch64/aligned_linker_script_arm.x
 [ALIGN] build_aarch64/aligned_linker_script_arm.x
 [LD] call_leaf_aarch64_aligned.out
/usr/local/popcorn/bin/x86_64-popcorn-linux-gnu-ld.gold -o call_leaf_aarch64_aligned.out call_leaf_aarch64.o -z noexecstack -z relro --hash-style=gnu --build-id -static -m aarch64linux -L~/musl-cross-make/output/aarch64-linux-musl/lib -L/usr/lib/gcc-cross/aarch64-linux-gnu/8 ~/musl-cross-make/output/aarch64-linux-musl/lib/crt1.o ~/musl-cross-make/output/aarch64-linux-musl/lib/libc.a ~/musl-cross-make/output/aarch64-linux-musl/lib/libm.a --start-group -lgcc -lgcc_eh --end-group -Map build_aarch64/aligned_map.txt -T build_aarch64/aligned_linker_script_arm.x
 [LD] call_leaf_x86_64_aligned.out
/usr/local/popcorn/bin/x86_64-popcorn-linux-gnu-ld.gold -o call_leaf_x86_64_aligned.out call_leaf_x86_64.o -z noexecstack -z relro --hash-style=gnu --build-id -static -m elf_x86_64 -L~/musl-cross-make/output/x86_64-linux-musl/lib ~/musl-cross-make/output/x86_64-linux-musl/lib/crt1.o ~/musl-cross-make/output/x86_64-linux-musl/lib/libc.a ~/musl-cross-make/output/x86_64-linux-musl/lib/libm.a --start-group --end-group -Map build_x86-64/aligned_map.txt -T build_x86-64/aligned_linker_script_x86.x
 [CHECK] Checking alignment for call_leaf_aarch64_aligned.out call_leaf_x86_64_aligned.out
python3.7 /usr/local/popcorn/bin/check-align.py call_leaf_aarch64_aligned.out call_leaf_x86_64_aligned.out
Error: '__set_thread_area' (t) not aligned (0x50402c vs. 0x503e7c)
Error: 'memcpy' (T) not aligned (0x503ea0 vs. 0x503e4a)
Error: 'memset' (T) not aligned (0x503d90 vs. 0x503d86)
rm call_leaf_opt.ll
