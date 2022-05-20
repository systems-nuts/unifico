POPCORN ?= /usr/local/popcorn

LLVM_TOOLCHAIN ?= ~/llvm-9/toolchain/bin

PROJECT_DIR ?= ../..

# Lib musl directories per architecture
MUSL_TOOLCHAIN ?= ~/musl-toolchains/llvm-9/
ARM64_MUSL	?= $(MUSL_TOOLCHAIN)/aarch64
X86_64_MUSL	?= $(MUSL_TOOLCHAIN)/x86-64

# Directory of libgcc & libgcc_eh for aarch64 compiler
ARM64_LIBGCC   ?= $(shell dirname \
									$(shell aarch64-linux-gnu-gcc -print-libgcc-file-name))

# For llvm-mca tool TODO
MCA	?= ~/llvm_13/toolchain/bin/llvm-mca
ARM64_CPU	?= thunderx2t99
X86_64_CPU	?= btver2
MCA_RESULT_DIR	?= ../mca-results/reg-pressure-O0
