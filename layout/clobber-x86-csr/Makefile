###############################################################################
# FIXME's
###############################################################################
BIN := clobber_x86

LLVM_TOOLCHAIN := ~/llvm_9/toolchain/bin

###############################################################################
# LLVM Tools and Flags
###############################################################################
CC  := $(LLVM_TOOLCHAIN)/clang
OPT := $(LLVM_TOOLCHAIN)/opt
LLC := $(LLVM_TOOLCHAIN)/llc

CFLAGS := -Xclang -disable-O0-optnone -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer -mno-red-zone 
OPT_FLAGS := -O0
LLC_FLAGS := -regalloc=fast


ifeq "$(shell gcc -dumpmachine)" "x86_64-linux-gnu"
	LLC_FLAGS += -x86-asm-syntax=intel
endif

######################################################

all: $(BIN).out $(BIN).s

######################################################

$(BIN).out: $(BIN).c
	$(CC) $(CFLAGS) -g -S -emit-llvm $(BIN).c -o $(BIN)_debug.ll
	$(OPT) $(OPT_FLAGS) -S $(BIN)_debug.ll -o $(BIN)_debug_opt.ll
	$(LLC) $(LLC_FLAGS) -filetype=obj $(BIN)_debug_opt.ll -o $(BIN).o
	$(CC) $(BIN).o -o $(BIN).out

######################################################

$(BIN).s: $(BIN).c
	$(CC) $(CFLAGS) -S -emit-llvm $(BIN).c -o $(BIN).ll
	$(OPT) $(OPT_FLAGS) -S $(BIN).ll -o $(BIN)_opt.ll
	$(LLC) $(LLC_FLAGS) $(BIN)_opt.ll -o $(BIN).s

######################################################

clean:
	rm *.ll *.o *.s *.out
