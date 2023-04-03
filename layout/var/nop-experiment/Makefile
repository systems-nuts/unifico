LLVM_TOOLCHAIN 	:= ~/llvm-9/toolchain/bin
CC  		 	:= $(LLVM_TOOLCHAIN)/clang

.PHONY: clean

all: nops.out

nops.out: nops.c
	$(CC) -g -O0 $^ -o $@

clean:
	rm *.out
