
OPT := -O0
FLAGS := $(OPT) -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer -mno-red-zone 
DEBUG_FLAGS := $(FLAGS) -g
ASSEMBLY_FLAGS := $(FLAGS) -S

c: call_leaf.out call_leaf.s call_leaf_2.out call_leaf_2.s

call_leaf.out: call_leaf.c
	clang $(DEBUG_FLAGS) call_leaf.c -o call_leaf.out

call_leaf.s: call_leaf.c
	clang -v $(ASSEMBLY_FLAGS) call_leaf.c -o call_leaf.s

call_leaf_2.out: call_leaf_2.o
	clang call_leaf_2.o -o call_leaf_2.out

call_leaf_2.o: call_leaf_debug.ll
	llc -filetype=obj call_leaf_debug.ll -o call_leaf_2.o

call_leaf_2.s: call_leaf.ll
	llc call_leaf.ll -o call_leaf_2.s

call_leaf_debug.ll: call_leaf.c
	clang $(ASSEMBLY_FLAGS) -g -emit-llvm -c call_leaf.c -o call_leaf_debug.ll

call_leaf.ll: call_leaf.c
	clang $(ASSEMBLY_FLAGS) -emit-llvm -c call_leaf.c -o call_leaf.ll

fact.out: fact.c
	clang $(DEBUG_FLAGS) fact.c -o fact.out

fact.s: fact.c
	clang $(ASSEMBLY_FLAGS) fact.c -o fact.s

fact_ll.s: fact.c
	llc fact.ll -o fact_ll.s

fact.ll: fact.c
	clang $(ASSEMBLY_FLAGS) -emit-llvm -S -c fact.c -o fact.ll

clobber_x86.out: clobber_x86.c
	clang $(DEBUG_FLAGS) clobber_x86.c -o clobber_x86.out

clobber_x86.s: clobber_x86.c
	clang $(ASSEMBLY_FLAGS) clobber_x86.c -o clobber_x86.s

main.s: main.ll
	llc main.ll -o main.s

main.ll: main.c
	clang -emit-llvm -S -c main.c -o main.ll

clean:
	rm *.ll *.s *.o *.out
