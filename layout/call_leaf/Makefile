
CFLAGS := -Xclang -disable-O0-optnone -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer -mno-red-zone 
OPT_FLAGS := O0
LLC_FLAGS := -O0

######################################################

call_leaf.s: call_leaf.c
	clang $(CFLAGS) -S -emit-llvm call_leaf.c -o call_leaf.ll
	opt -$(OPT_FLAGS) -S call_leaf.ll -o call_leaf_opt.ll
	llc $(LLC_FLAGS) call_leaf_opt.ll -o $(OPT_FLAGS)_call_leaf.s

######################################################

clean:
	rm *.ll 
