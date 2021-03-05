rm -rf build_aarch64/
rm -rf build_x86-64/
mkdir -p build_aarch64/
mkdir -p build_x86-64/

# clang
for FILE in $(ls *.c); do
	FILE=${FILE%%.*}
	/usr/local/popcorn/bin/clang -O0 -Wall -nostdinc -g -fno-common -ftls-model=initial-exec -c -isystem /usr/local/popcorn/aarch64/include -emit-llvm -S $FILE.c -o $FILE.x86_64.clang.no-popcorn.ll
done

# llvm-link
/usr/local/popcorn/bin/llvm-link -S -o x86_64.clang.no-popcorn.ll *.x86_64.clang.no-popcorn.ll

# Remove the x86-64-related information
grep "x86-64" x86_64.clang.no-popcorn.ll
sed -e "s/\"target-cpu\"\=\"x86-64\"\ \"target-features\"\=\"+cx8,+fxsr,+mmx,+sse,+sse2,+x87\"//g" -i.backup x86_64.clang.no-popcorn.ll
grep "x86-64" x86_64.clang.no-popcorn.ll 
cp x86_64.clang.no-popcorn.ll clang.no-popcorn.ll 

# opt
/usr/local/popcorn/bin/opt -tti -targetlibinfo -assumption-cache-tracker -profile-summary-info -popcorn-compat -domtree -loops -looppaths -scalar-evolution -select-migration-points --name-string-literals --static-var-sections  -forceattrs -basiccg -always-inline -S clang.no-popcorn.ll -o opt-with-popcorn-passes.ll 

# llc --popcorn-instrument=migration -optimize-regalloc -fast-isel=false -disable-machine-cse
/usr/local/popcorn/bin/llc -relocation-model=pic --trap-unreachable --popcorn-instrument=migration -optimize-regalloc -fast-isel=false -disable-machine-cse -march=x86-64 -no-x86-call-frame-opt -O0 -filetype=obj -o x86_64.llc.o opt-with-popcorn-passes.ll
/usr/local/popcorn/bin/llc -relocation-model=pic --trap-unreachable --popcorn-instrument=migration -optimize-regalloc -fast-isel=false -disable-machine-cse -march=aarch64 -O0 -filetype=obj -o aarch64.llc.o opt-with-popcorn-passes.ll 

# link (unaligned) -> map files
/usr/local/popcorn/bin/aarch64-popcorn-linux-gnu-ld.gold -o build_aarch64/call_leaf_aarch64 aarch64.llc.o -z noexecstack -z relro --hash-style=gnu --build-id -static -m aarch64linux -L/usr/local/popcorn/aarch64/lib -L/usr/lib/gcc-cross/aarch64-linux-gnu/8 /usr/local/popcorn/aarch64/lib/crt1.o /usr/local/popcorn/aarch64/lib/libc.a /usr/local/popcorn/aarch64/lib/libmigrate.a /usr/local/popcorn/aarch64/lib/libstack-transform.a /usr/local/popcorn/aarch64/lib/libelf.a /usr/local/popcorn/aarch64/lib/libpthread.a /usr/local/popcorn/aarch64/lib/libc.a /usr/local/popcorn/aarch64/lib/libm.a --start-group -lgcc -lgcc_eh --end-group -Map build_aarch64/map.txt
/usr/local/popcorn/bin/x86_64-popcorn-linux-gnu-ld.gold -o build_x86-64/call_leaf_x86-64 x86_64.llc.o -z noexecstack -z relro --hash-style=gnu --build-id -static -m elf_x86_64 -L/usr/local/popcorn/x86_64/lib /usr/local/popcorn/x86_64/lib/crt1.o /usr/local/popcorn/x86_64/lib/libc.a /usr/local/popcorn/x86_64/lib/libmigrate.a /usr/local/popcorn/x86_64/lib/libstack-transform.a /usr/local/popcorn/x86_64/lib/libelf.a /usr/local/popcorn/x86_64/lib/libpthread.a /usr/local/popcorn/x86_64/lib/libc.a /usr/local/popcorn/x86_64/lib/libm.a --start-group --end-group -Map build_x86-64/map.txt

# pyalign -> link script
/usr/local/popcorn/bin/pyalign --compiler-inst /usr/local/popcorn --x86-bin build_x86-64/call_leaf_x86-64 --arm-bin build_aarch64/call_leaf_aarch64 --x86-map build_x86-64/map.txt --arm-map build_aarch64/map.txt --output-x86-ls build_x86-64/aligned_linker_script_x86.x --output-arm-ls build_aarch64/aligned_linker_script_arm.x

# link (aligned)
/usr/local/popcorn/bin/aarch64-popcorn-linux-gnu-ld.gold -o call_leaf_aarch64 aarch64.llc.o -z noexecstack -z relro --hash-style=gnu --build-id -static -m aarch64linux -L/usr/local/popcorn/aarch64/lib -L/usr/lib/gcc-cross/aarch64-linux-gnu/8 /usr/local/popcorn/aarch64/lib/crt1.o /usr/local/popcorn/aarch64/lib/libc.a /usr/local/popcorn/aarch64/lib/libmigrate.a /usr/local/popcorn/aarch64/lib/libstack-transform.a /usr/local/popcorn/aarch64/lib/libelf.a /usr/local/popcorn/aarch64/lib/libpthread.a /usr/local/popcorn/aarch64/lib/libc.a /usr/local/popcorn/aarch64/lib/libm.a --start-group -lgcc -lgcc_eh --end-group -Map build_aarch64/aligned_map.txt -T build_aarch64/aligned_linker_script_arm.x
/usr/local/popcorn/bin/x86_64-popcorn-linux-gnu-ld.gold -o call_leaf_x86-64 x86_64.llc.o -z noexecstack -z relro --hash-style=gnu --build-id -static -m elf_x86_64 -L/usr/local/popcorn/x86_64/lib /usr/local/popcorn/x86_64/lib/crt1.o /usr/local/popcorn/x86_64/lib/libc.a /usr/local/popcorn/x86_64/lib/libmigrate.a /usr/local/popcorn/x86_64/lib/libstack-transform.a /usr/local/popcorn/x86_64/lib/libelf.a /usr/local/popcorn/x86_64/lib/libpthread.a /usr/local/popcorn/x86_64/lib/libc.a /usr/local/popcorn/x86_64/lib/libm.a --start-group --end-group -Map build_x86-64/aligned_map.txt -T build_x86-64/aligned_linker_script_x86.x
