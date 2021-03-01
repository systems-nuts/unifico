###############################################################################
# FIXME's
###############################################################################
POPCORN 	   := /usr/local/popcorn
LLVM_TOOLCHAIN := /usr/local/popcorn/bin

# Directory of libgcc & libgcc_eh for aarch64 compiler
ARM64_LIBGCC   := $(shell dirname \
	                $(shell aarch64-linux-gnu-gcc -print-libgcc-file-name))

BIN := call_leaf
SRC := $(BIN).c

###############################################################################
# LLVM Tools and Flags
###############################################################################
CC  := $(LLVM_TOOLCHAIN)/clang
OPT := $(LLVM_TOOLCHAIN)/opt
LLC := $(LLVM_TOOLCHAIN)/llc

CFLAGS 		:= -Xclang -disable-O0-optnone #-fno-omit-frame-pointer -mno-omit-leaf-frame-pointer -mno-red-zone
CFLAGS 		+= -O0 -Wall -nostdinc
HET_CFLAGS 	:= $(CFLAGS) -fno-common -ftls-model=initial-exec
OPT_FLAGS 	:= -name-string-literals -static-var-sections
LLC_FLAGS 	:= -function-sections -data-sections
#LLC_FLAGS 	+= -relocation-model=pic --trap-unreachable -optimize-regalloc -fast-isel=false -disable-machine-cse

IR := $(SRC:.c=.ll)

###############################################################################
# Linker and Flags
###############################################################################
LD       := $(POPCORN)/bin/x86_64-popcorn-linux-gnu-ld.bfd
ARM64_LD := $(POPCORN)/bin/aarch64-popcorn-linux-gnu-ld.bfd

LDFLAGS := -z noexecstack -z relro --hash-style=gnu --build-id -static
LIBS    := /lib/crt1.o \
           /lib/libc.a \
           /lib/libm.a

LIBGCC := --start-group -lgcc -lgcc_eh --end-group

###############################################################################
# Alignment
###############################################################################
ALIGN := $(POPCORN)/bin/pyalign

###############################################################################
# X86-64
###############################################################################
X86_64_POPCORN     := $(POPCORN)/x86_64
X86_64_BUILD       := build_x86-64
X86_64_ALIGNED     := $(BIN)_x86-64_aligned.out
X86_64_UNALIGNED   := $(BIN)_x86-64_unaligned.out
X86_64_OBJ         := $(SRC:.c=_x86-64.o)
X86_64_MAP         := $(X86_64_BUILD)/map.txt
X86_64_LD_SCRIPT   := $(X86_64_BUILD)/aligned_linker_script_x86.x
X86_64_ALIGNED_MAP := $(X86_64_BUILD)/aligned_map.txt

X86_64_TARGET  := x86_64-linux-gnu
X86_64_INC     := -isystem $(X86_64_POPCORN)/include
X86_64_LDFLAGS := -m elf_x86_64 -L$(X86_64_POPCORN)/lib \
                  $(addprefix $(X86_64_POPCORN),$(LIBS)) \
                  --start-group --end-group

###############################################################################
# Aarch64
###############################################################################
ARM64_POPCORN 	  := $(POPCORN)/aarch64
ARM64_BUILD       := build_aarch64
ARM64_ALIGNED     := $(BIN)_aarch64_aligned.out
ARM64_UNALIGNED   := $(BIN)_aarch64_unaligned.out
ARM64_OBJ         := $(SRC:.c=_aarch64.o)
ARM64_MAP         := $(ARM64_BUILD)/map.txt
ARM64_LD_SCRIPT   := $(ARM64_BUILD)/aligned_linker_script_arm.x
ARM64_ALIGNED_MAP := $(ARM64_BUILD)/aligned_map.txt

ARM64_TARGET  := aarch64-linux-gnu
ARM64_INC     := -isystem $(ARM64_POPCORN)/include
ARM64_LDFLAGS := -m aarch64linux -L$(ARM64_POPCORN)/lib -L$(ARM64_LIBGCC) \
	                 $(addprefix $(ARM64_POPCORN),$(LIBS)) $(LIBGCC)

###############################################################################
#                                 Recipes                                     #
###############################################################################

all: aligned

ir: $(IR)

aligned: aligned-x86-64 aligned-aarch64
unaligned: unaligned-x86-64 unaligned-aarch64

aligned-x86-64: $(X86_64_ALIGNED)
unaligned-x86-64: $(X86_64_UNALIGNED)
obj-x86-64:  	$(X86_64_OBJ)

aligned-aarch64: $(ARM64_ALIGNED)
unaligned-aarch64: $(ARM64_UNALIGNED)
obj-aarch64:  	$(ARM64_OBJ)

##########
# Common #
##########

%.ll: %.c
	@echo " [IR] $@"
	$(CC) $(HET_CFLAGS) -g -S -emit-llvm $(ARM64_INC) -o $@ $<
	# Remove the x86-64-related information
	sed -e "s/\"target-cpu\"\=\"x86-64\"\ \"target-features\"\=\"+cx8,+fxsr,+mmx,+sse,+sse2,+x87\"//g" -i.backup $@
	# Make directories
	mkdir -p $(X86_64_BUILD) $(ARM64_BUILD)

%_opt.ll: %.ll
	@echo " [OPT] $@"
	$(OPT) $(OPT_FLAGS) -S -o $@ $<

###########
# AArch64 #
###########

%_aarch64.o: %_opt.ll
	@echo " [LLC] $@"
	$(LLC) $(LLC_FLAGS) $(HET_FLAGS) -march=aarch64 -filetype=obj -o $(<:_opt.ll=_aarch64.o) $<

$(ARM64_UNALIGNED): $(ARM64_OBJ)
	@echo " [LD] $@"
	$(ARM64_LD) -o $@ $< $(LDFLAGS) $(ARM64_LDFLAGS) -Map $(ARM64_MAP)

$(ARM64_LD_SCRIPT): $(X86_64_LD_SCRIPT)
	@echo " [ALIGN] $@"

$(ARM64_ALIGNED): $(ARM64_LD_SCRIPT)
	@echo " [LD] $@"
	$(ARM64_LD) -o $@ $(ARM64_OBJ) $(LDFLAGS) $(ARM64_LDFLAGS) -Map $(ARM64_ALIGNED_MAP) -T $<

##########
# x86-64 #
##########

%_x86-64.o: %_opt.ll
	@echo " [LLC] $@"
	$(LLC) $(LLC_FLAGS) $(HET_FLAGS) -march=x86-64 -filetype=obj -o $(<:_opt.ll=_x86-64.o) $<

$(X86_64_UNALIGNED): $(X86_64_OBJ)
	@echo " [LD] $@"
	$(LD) -o $@ $< $(LDFLAGS) $(X86_64_LDFLAGS) -Map $(X86_64_MAP)

$(X86_64_LD_SCRIPT): $(ARM64_UNALIGNED) $(X86_64_UNALIGNED)
	@echo " [ALIGN] $@"
	$(ALIGN) --compiler-inst $(POPCORN) \
		--x86-bin $(X86_64_UNALIGNED) --arm-bin $(ARM64_UNALIGNED) \
		--x86-map $(X86_64_MAP) --arm-map $(ARM64_MAP) \
		--output-x86-ls $(X86_64_LD_SCRIPT) --output-arm-ls $(ARM64_LD_SCRIPT)

$(X86_64_ALIGNED): $(X86_64_LD_SCRIPT)
	@echo " [LD] $@"
	$(LD) -o $@ $(X86_64_OBJ) $(LDFLAGS) $(X86_64_LDFLAGS) -Map $(X86_64_ALIGNED_MAP) -T $<

clean:
	@echo " [CLEAN] $(ARM64_ALIGNED) $(ARM64_BUILD) $(X86_64_ALIGNED) \
		$(X86_64_BUILD) $(X86_64_LD_SCRIPT) $(ARM64_LD_SCRIPT) *.ll *.o"
	@rm -rf $(ARM64_ALIGNED) $(ARM64_BUILD) $(X86_64_ALIGNED) $(X86_64_BUILD) \
		$(X86_64_SD_BUILD) $(X86_64_LD_SCRIPT) $(ARM64_LD_SCRIPT) *.ll *.o

.PHONY: all clean \
        aligned aligned-aarch64 aligned-x86-64 \
        unaligned aligned-aarch64 aligned-x86-64

######################################################

call_leaf.s: call_leaf.c
	clang $(CFLAGS) -S -emit-llvm call_leaf.c -o call_leaf.ll
	$(OPT) $(OPT_FLAGS) -S call_leaf.ll -o call_leaf_opt.ll
	$(LLC) $(LLC_FLAGS) call_leaf_opt.ll -o call_leaf$(subst =,_,$(OPT_FLAGS))$(subst =,_,$(LLC_FLAGS)).s

######################################################
