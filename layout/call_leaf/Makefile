
CFLAGS := -Xclang -disable-O0-optnone -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer -mno-red-zone 
OPT_FLAGS := -O0
LLC_FLAGS := -O0

######################################################

all: call_leaf.out call_leaf.s

######################################################

call_leaf.out: call_leaf.c
	clang $(CFLAGS) -g -S -emit-llvm call_leaf.c -o call_leaf_debug.ll
	opt $(OPT_FLAGS) -S call_leaf_debug.ll -o call_leaf_debug_opt.ll
	llc $(LLC_FLAGS) -filetype=obj call_leaf_debug_opt.ll -o call_leaf_2.o
	clang call_leaf_2.o -o call_leaf.out

######################################################

call_leaf.s: call_leaf.c
	clang $(CFLAGS) -S -emit-llvm call_leaf.c -o call_leaf.ll
	opt $(OPT_FLAGS) -S call_leaf.ll -o call_leaf_opt.ll
	llc $(LLC_FLAGS) call_leaf_opt.ll -o call_leaf$(subst =,_,$(OPT_FLAGS))$(subst =,_,$(LLC_FLAGS)).s

######################################################

clean:
	rm *.ll *.out
