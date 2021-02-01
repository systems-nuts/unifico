
CFLAGS := -O0 -g -Xclang -disable-O0-optnone -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer -mno-red-zone 
OPT_FLAGS := -mem2reg 
LLC_FLAGS := -O2

c: call_leaf.out call_leaf.s call_leaf_2.out call_leaf_2.s

f: fact.out fact.s fact_2.out fact_2.s 

######################################################

call_leaf_2.out: call_leaf.c
	clang $(CFLAGS) -g -S -emit-llvm call_leaf.c -o call_leaf_debug.ll
	opt $(OPT_FLAGS) -S call_leaf_debug.ll -o call_leaf_debug_opt.ll
	llc $(LLC_FLAGS) -filetype=obj call_leaf_debug_opt.ll -o call_leaf_2.o
	clang call_leaf_2.o -o call_leaf_2.out

call_leaf_2.s: call_leaf.c
	clang $(CFLAGS) -S -emit-llvm call_leaf.c -o call_leaf.ll
	opt $(OPT_FLAGS) -S call_leaf.ll -o call_leaf_opt.ll
	llc $(LLC_FLAGS) call_leaf_opt.ll -o call_leaf_2.s

call_leaf.out: call_leaf.c
	clang $(CFLAGS) -g call_leaf.c -o call_leaf.out

call_leaf.s: call_leaf.c
	clang $(CFLAGS) -S call_leaf.c -o call_leaf.s

######################################################

fact_2.out: fact.c
	clang $(CFLAGS) -g -S -emit-llvm fact.c -o fact_debug.ll
	opt $(OPT_FLAGS) -S fact_debug.ll -o fact_debug_opt.ll
	llc $(LLC_FLAGS) -filetype=obj fact_debug_opt.ll -o fact_2.o
	clang fact_2.o -o fact_2.out

fact_2.s: fact.c
	clang $(CFLAGS) -S -emit-llvm fact.c -o fact.ll
	opt $(OPT_FLAGS) -S fact.ll -o fact_opt.ll
	llc $(LLC_FLAGS) fact_opt.ll -o fact_2.s

fact.out: fact.c
	clang $(CFLAGS) -g fact.c -o fact.out

fact.s: fact.c
	clang $(CFLAGS) -S fact.c -o fact.s

######################################################

clobber_x86.out: clobber_x86.c
	clang $(CFLAGS) -g clobber_x86.c -o clobber_x86.out

clobber_x86.s: clobber_x86.c
	clang $(CFLAGS) -S clobber_x86.c -o clobber_x86.s

main.s: main.ll
	llc main.ll -o main.s

main.ll: main.c
	clang -emit-llvm -S -c main.c -o main.ll

clean:
	rm *.ll *.s *.o *.out
