
CFLAGS := -Xclang -disable-O0-optnone -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer -mno-red-zone 
OPT_FLAGS := -O0
LLC_FLAGS := -O0

######################################################

all: fact.out fact.s

######################################################

fact.out: fact.c
	clang $(CFLAGS) -g -S -emit-llvm fact.c -o fact_debug.ll
	opt $(OPT_FLAGS) -S fact_debug.ll -o fact_debug_opt.ll
	llc $(LLC_FLAGS) -filetype=obj fact_debug_opt.ll -o fact_2.o
	clang fact_2.o -o fact.out

######################################################

fact.s: fact.c
	clang $(CFLAGS) -S -emit-llvm fact.c -o fact.ll
	opt $(OPT_FLAGS) -S fact.ll -o fact_opt.ll
	llc $(LLC_FLAGS) fact_opt.ll -o fact$(subst =,_,$(OPT_FLAGS))$(subst =,_,$(LLC_FLAGS)).s

######################################################

clean:
	rm *.ll *.out
