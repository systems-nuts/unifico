
CFLAGS := -O0 -Xclang -disable-O0-optnone -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer -mno-red-zone 
OPT_FLAGS := -mem2reg
LLC_FLAGS := -regalloc=fast 
OBJ := bubble_sort

ifeq "$(gcc -dumpmachine)" "x86_64-linux-gnu"
	LLC_FLAGS += -x86-asm-syntax=intel
endif

.PHONY: all clean

all: $(OBJ)

bubble_sort: bubble_sort.c
	clang $(CFLAGS) -g -S -emit-llvm bubble_sort.c -o bubble_sort_debug.ll
	opt $(OPT_FLAGS) -S bubble_sort_debug.ll -o bubble_sort_debug_opt.ll
	llc $(LLC_FLAGS) -filetype=obj bubble_sort_debug_opt.ll -o bubble_sort.o
	clang bubble_sort_2.o -o bubble_sort.out
	############################################################
	clang $(CFLAGS) -S -emit-llvm bubble_sort.c -o bubble_sort.ll
	opt $(OPT_FLAGS) -S bubble_sort.ll -o bubble_sort_opt.ll
	llc $(LLC_FLAGS) bubble_sort_opt.ll -o bubble_sort.s

clean:
	rm *.ll *.s *.o *.out
