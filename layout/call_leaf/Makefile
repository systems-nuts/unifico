
# FIXME's 
BIN := call_leaf
SRC := $(BIN).c
POPCORN := /usr/local/popcorn
X86_64_POPCORN := $(POPCORN)/x86_64
ARM64_POPCORN := $(POPCORN)/aarch64
LIBGCC  := --start-group -lgcc -lgcc_eh --end-group
ARM64_LIBGCC := $(shell dirname \
	                $(shell aarch64-linux-gnu-gcc -print-libgcc-file-name))

# Tools
# LD := ld.gold
LD := /usr/local/popcorn/bin/x86_64-popcorn-linux-gnu-ld.gold
ALIGN := $(POPCORN)/bin/pyalign

# Flags
CFLAGS := -Xclang -disable-O0-optnone -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer -mno-red-zone 
OPT_FLAGS := -name-string-literals -static-var-sections
LLC_FLAGS := -function-sections -data-sections
LDFLAGS := -z noexecstack -z relro --hash-style=gnu --build-id 
LIBS    := /lib/crt1.o \
	/lib/libc.a \
	/lib/libm.a

X86_64_LDFLAGS := -m elf_x86_64 -L$(X86_64_POPCORN)/lib \
                  $(addprefix $(X86_64_POPCORN),$(LIBS)) \
                  --start-group --end-group
ARM64_LDFLAGS := -m aarch64linux -L$(ARM64_POPCORN)/lib -L$(ARM64_LIBGCC) \
	                 $(addprefix $(ARM64_POPCORN),$(LIBS)) $(LIBGCC)

# X86-64
X86_64_BUILD       := build_x86-64
X86_64_ALIGNED     := $(BIN)_x86-64_aligned.out
X86_64_UNALIGNED   := $(BIN)_x86-64_unaligned.out
X86_64_OBJ         := $(SRC:.c=_x86_64.o)
X86_64_MAP         := $(X86_64_BUILD)/map.txt
X86_64_LD_SCRIPT   := $(X86_64_BUILD)/aligned_linker_script_x86.x
X86_64_ALIGNED_MAP := $(X86_64_BUILD)/aligned_map.txt

# Aarch64
ARM64_BUILD       := build_aarch64
ARM64_ALIGNED     := $(BIN)_aarch64_aligned.out
ARM64_UNALIGNED   := $(BIN)_aarch64_unaligned.out
ARM64_MAP         := $(ARM64_BUILD)/map.txt
ARM64_LD_SCRIPT   := $(ARM64_BUILD)/aligned_linker_script_arm.x
ARM64_ALIGNED_MAP := $(ARM64_BUILD)/aligned_map.txt

###############################################################################
#                                 Recipes                                     #
###############################################################################

aligned: aligned-x86-64 aligned-aarch64
unaligned: unaligned-x86-64 unaligned-aarch64

aligned-x86-64: $(X86_64_ALIGNED)
unaligned-x86-64: $(X86_64_UNALIGNED)
obj-x86-64:  	$(X86_64_OBJ)

aligned-aarch64: $(ARM64_ALIGNED)
unaligned-aarch64: $(ARM64_UNALIGNED)
obj-aarch64:  	$(ARM64_OBJ)

######################################################

all: call_leaf.out call_leaf.s

######################################################

call_leaf_x86.ll: call_leaf.c
	@echo " [CC] $@"
	clang $(CFLAGS) -g -S -emit-llvm -ffunction-sections -fdata-sections call_leaf.c -o call_leaf_x86.ll 
	# Remove the x86-64-related information
	sed -e "s/\"target-cpu\"\=\"x86-64\"\ \"target-features\"\=\"+cx8,+fxsr,+mmx,+sse,+sse2,+x87\"//g" -i.backup call_leaf_x86.ll

call_leaf_x86_opt.ll: call_leaf_x86.ll
	@echo " [OPT] $@"
	opt $(OPT_FLAGS) -S call_leaf_x86.ll -o call_leaf_x86_opt.ll 

call_leaf_x86.o: call_leaf_x86_opt.ll
	@echo " [LLC] $@ (x86-64)"
	llc $(LLC_FLAGS) -filetype=obj call_leaf_x86_opt.ll -o call_leaf_x86.o

$(X86_64_UNALIGNED): call_leaf_x86.o
	@echo " [LD] $@ (x86-64 unaligned)"
	$(LD) -o $@ $^ $(LDFLAGS) $(X86_64_LDFLAGS) -Map $(X86_64_MAP)

call_leaf_aarch64.o: call_leaf_x86_opt.ll
	@echo " [LLC] $@ (aarch64)"
	llc $(LLC_FLAGS) -march=aarch64 -filetype=obj call_leaf_x86_opt.ll -o call_leaf_aarch64.o

$(ARM64_UNALIGNED): call_leaf_aarch64.o
	@echo " [LD] $@ (aarch64 unaligned)"
	$(LD) -o $@ $^ $(LDFLAGS) $(ARM64_LDFLAGS) -Map $(ARM64_MAP)

$(X86_64_LD_SCRIPT): unaligned
	@echo " [ALIGN] $@"
	$(ALIGN) --compiler-inst /usr/local/popcorn --x86-bin $(X86_64_UNALIGNED) --arm-bin $(ARM64_UNALIGNED) --x86-map $(X86_64_MAP) --arm-map $(ARM64_MAP) --output-x86-ls $(X86_64_LD_SCRIPT) --output-arm-ls $(ARM64_LD_SCRIPT)

$(ARM64_LD_SCRIPT): $(X86_64_LD_SCRIPT)

$(X86_64_ALIGNED): $(X86_64_LD_SCRIPT)
	@echo " [LD] $@ (x86-64 aligned)"
	$(LD) -o $@ call_leaf_x86.o $(LDFLAGS) $(X86_64_LDFLAGS) -Map $(X86_64_ALIGNED_MAP) -T $<

$(ARM64_ALIGNED): $(ARM64_LD_SCRIPT)
	@echo " [LD] $@ (aarch64 aligned)"
	$(LD) -o $@ call_leaf_aarch64.o $(LDFLAGS) $(ARM64_LDFLAGS) -Map $(ARM64_ALIGNED_MAP) -T $<

######################################################

call_leaf.s: call_leaf.c
	clang $(CFLAGS) -S -emit-llvm call_leaf.c -o call_leaf.ll
	opt $(OPT_FLAGS) -S call_leaf.ll -o call_leaf_opt.ll
	llc $(LLC_FLAGS) call_leaf_opt.ll -o call_leaf$(subst =,_,$(OPT_FLAGS))$(subst =,_,$(LLC_FLAGS)).s

######################################################

clean:
	@echo " [CLEAN]"
	rm *.o *.ll *.out
	rm -r build_*/*
