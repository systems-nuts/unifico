
OPT := -O0
FLAGS := $(OPT) -mgeneral-regs-only -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer -mno-red-zone
DEBUG_FLAGS := $(FLAGS) -g
ASSEMBLY_FLAGS := $(FLAGS) -S -g

fact.out: fact.c
	clang $(DEBUG_FLAGS) fact.c -o fact.out

fact.s: fact.c
	clang $(ASSEMBLY_FLAGS) fact.c -o fact.s

clobber_x86.out: clobber_x86.c
	clang $(DEBUG_FLAGS) clobber_x86.c -o clobber_x86.out

clobber_x86.s: clobber_x86.c
	clang $(ASSEMBLY_FLAGS) clobber_x86.c -o clobber_x86.s

call_leaf.out: call_leaf.c
	clang $(DEBUG_FLAGS) call_leaf.c -o call_leaf.out

call_leaf.s: call_leaf.c
	clang $(ASSEMBLY_FLAGS) call_leaf.c -o call_leaf.s

main.s: main.ll
	llc main.ll -o main.s

main.ll: main.c
	clang -emit-llvm -S -c main.c -o main.ll

clean:
	rm *.ll *.s *.out 
