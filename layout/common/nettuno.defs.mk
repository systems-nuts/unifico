POPCORN ?= /usr/local/popcorn

# Generic UNMODIFIED flag
ifdef UNMODIFIED
UNMODIFIED_LLVM := 1
UNMODIFIED_MUSL := 1
endif

# LLVM Toolchain
ifdef UNMODIFIED_LLVM
LLVM_TOOLCHAIN ?= ~/llvm-9.0.1/toolchain/bin
else
LLVM_TOOLCHAIN ?= ~/llvm-9/toolchain/bin
endif

PROJECT_DIR ?= ../..

# Lib musl directories per architecture
ifdef UNMODIFIED_MUSL
MUSL_TOOLCHAIN ?= ~/musl-toolchains/unmodified
else
MUSL_TOOLCHAIN ?= ~/musl-toolchains/criu-3
endif

ARM64_MUSL	?= $(MUSL_TOOLCHAIN)/aarch64
X86_64_MUSL	?= $(MUSL_TOOLCHAIN)/x86_64

# Directory of libgcc & libgcc_eh for aarch64 compiler
ARM64_LIBGCC   ?= $(shell dirname \
									$(shell aarch64-linux-gnu-gcc -print-libgcc-file-name))

# Various configurations
SSHPASS_IGNORE =
UNMODIFIED ?=
LLC_PASSES_TO_DEBUG =
