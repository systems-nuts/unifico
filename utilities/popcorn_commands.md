# download repo
git clone https://gitlab.com/khordadi/npb ~/npb
cd ~/npb
make clean
make A
# npb is
cd ~/npb/is
mkdir -p build_aarch64/
mkdir -p build_x86-64/
# compile
/usr/local/popcorn/bin/clang -O0 -Wall -nostdinc -g -popcorn-migratable -fno-common -ftls-model=initial-exec -c -isystem /usr/local/popcorn/aarch64/include -o is.o is.c
/usr/local/popcorn/bin/clang -O0 -Wall -nostdinc -g -popcorn-migratable -fno-common -ftls-model=initial-exec -c -isystem /usr/local/popcorn/aarch64/include -o c_timers.o c_timers.c
/usr/local/popcorn/bin/clang -O0 -Wall -nostdinc -g -popcorn-migratable -fno-common -ftls-model=initial-exec -c -isystem /usr/local/popcorn/aarch64/include -o c_print_results.o c_print_results.c
/usr/local/popcorn/bin/clang -O0 -Wall -nostdinc -g -popcorn-migratable -fno-common -ftls-model=initial-exec -c -isystem /usr/local/popcorn/aarch64/include -o wtime.o wtime.c
# link (unaligned) -> map files
/usr/local/popcorn/bin/aarch64-popcorn-linux-gnu-ld.bfd -o build_aarch64/is_aarch64 is_aarch64.o c_timers_aarch64.o c_print_results_aarch64.o wtime_aarch64.o -z noexecstack -z relro --hash-style=gnu --build-id -static -m aarch64linux -L/usr/local/popcorn/aarch64/lib -L/usr/lib/gcc-cross/aarch64-linux-gnu/8 /usr/local/popcorn/aarch64/lib/crt1.o /usr/local/popcorn/aarch64/lib/libc.a /usr/local/popcorn/aarch64/lib/libmigrate.a /usr/local/popcorn/aarch64/lib/libstack-transform.a /usr/local/popcorn/aarch64/lib/libelf.a /usr/local/popcorn/aarch64/lib/libpthread.a /usr/local/popcorn/aarch64/lib/libc.a /usr/local/popcorn/aarch64/lib/libm.a --start-group -lgcc -lgcc_eh --end-group -Map build_aarch64/map.txt
/usr/local/popcorn/bin/x86_64-popcorn-linux-gnu-ld.bfd -o build_x86-64/is_x86-64 is_x86_64.o c_timers_x86_64.o c_print_results_x86_64.o wtime_x86_64.o -z noexecstack -z relro --hash-style=gnu --build-id -static -m elf_x86_64 -L/usr/local/popcorn/x86_64/lib /usr/local/popcorn/x86_64/lib/crt1.o /usr/local/popcorn/x86_64/lib/libc.a /usr/local/popcorn/x86_64/lib/libmigrate.a /usr/local/popcorn/x86_64/lib/libstack-transform.a /usr/local/popcorn/x86_64/lib/libelf.a /usr/local/popcorn/x86_64/lib/libpthread.a /usr/local/popcorn/x86_64/lib/libc.a /usr/local/popcorn/x86_64/lib/libm.a --start-group --end-group -Map build_x86-64/map.txt
# pyalign -> link script
/usr/local/popcorn/bin/pyalign --compiler-inst /usr/local/popcorn --x86-bin build_x86-64/is_x86-64 --arm-bin build_aarch64/is_aarch64 --x86-map build_x86-64/map.txt --arm-map build_aarch64/map.txt --output-x86-ls build_x86-64/aligned_linker_script_x86.x --output-arm-ls build_aarch64/aligned_linker_script_arm.x
# link (aligned)
/usr/local/popcorn/bin/aarch64-popcorn-linux-gnu-ld.bfd -o is_aarch64 is_aarch64.o c_timers_aarch64.o c_print_results_aarch64.o wtime_aarch64.o -z noexecstack -z relro --hash-style=gnu --build-id -static -m aarch64linux -L/usr/local/popcorn/aarch64/lib -L/usr/lib/gcc-cross/aarch64-linux-gnu/8 /usr/local/popcorn/aarch64/lib/crt1.o /usr/local/popcorn/aarch64/lib/libc.a /usr/local/popcorn/aarch64/lib/libmigrate.a /usr/local/popcorn/aarch64/lib/libstack-transform.a /usr/local/popcorn/aarch64/lib/libelf.a /usr/local/popcorn/aarch64/lib/libpthread.a /usr/local/popcorn/aarch64/lib/libc.a /usr/local/popcorn/aarch64/lib/libm.a --start-group -lgcc -lgcc_eh --end-group -Map build_aarch64/aligned_map.txt -T build_aarch64/aligned_linker_script_arm.x
/usr/local/popcorn/bin/x86_64-popcorn-linux-gnu-ld.bfd -o is_x86-64 is_x86_64.o c_timers_x86_64.o c_print_results_x86_64.o wtime_x86_64.o -z noexecstack -z relro --hash-style=gnu --build-id -static -m elf_x86_64 -L/usr/local/popcorn/x86_64/lib /usr/local/popcorn/x86_64/lib/crt1.o /usr/local/popcorn/x86_64/lib/libc.a /usr/local/popcorn/x86_64/lib/libmigrate.a /usr/local/popcorn/x86_64/lib/libstack-transform.a /usr/local/popcorn/x86_64/lib/libelf.a /usr/local/popcorn/x86_64/lib/libpthread.a /usr/local/popcorn/x86_64/lib/libc.a /usr/local/popcorn/x86_64/lib/libm.a --start-group --end-group -Map build_x86-64/aligned_map.txt -T build_x86-64/aligned_linker_script_x86.x
# metadata generation
/usr/local/popcorn/bin/gen-stackinfo -f is_aarch64
/usr/local/popcorn/bin/gen-stackinfo -f is_x86-64