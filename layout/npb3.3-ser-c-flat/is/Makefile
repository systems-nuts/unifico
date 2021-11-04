BIN := is

SRC := is.c c_timers.c c_print_results.c wtime.c

#LLVM_TOOLCHAIN = ~/llvm-9-align/toolchain/bin
LLVM_TOOLCHAIN = ~/llvm-9/toolchain/bin

#MUSL_TOOLCHAIN = ~/musl-toolchains/llvm-9-align
MUSL_TOOLCHAIN = ~/musl-toolchains/llvm-9

include ../../common/common.mk

#LLC_FLAGS += -disable-machine-licm 
LLC_FLAGS += -no-x86-call-frame-opt 
LLC_FLAGS += -join-liveintervals=false 
#LLC_FLAGS += -code-model=large
