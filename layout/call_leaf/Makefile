
# FIXME's 
BIN := call_leaf
SRC := $(BIN).c
POPCORN := /usr/local/popcorn

# Tools
LD := ld.gold
ALIGN := $(POPCORN)/bin/pyalign

# Flags
CFLAGS := -Xclang -disable-O0-optnone -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer -mno-red-zone 
OPT_FLAGS := -O0
LLC_FLAGS := -O0
LDFLAGS := -z noexecstack -z relro --hash-style=gnu --build-id 

X86_64_LDFLAGS := -m elf_x86_64 -L$(X86_64_POPCORN)/lib \
                  $(addprefix $(X86_64_POPCORN),$(LIBS)) \
                  --start-group --end-group

# X86-64
X86_64_ALIGNED     := $(BIN)_x86-64_aligned
X86_64_VANILLA     := $(BIN)_x86-64_vanilla
X86_64_OBJ         := $(SRC:.c=_x86_64.o)
X86_64_MAP         := x86-64_map.txt
X86_64_LD_SCRIPT   := aligned_linker_script_x86.x
X86_64_ALIGNED_MAP := aligned_x86-64_map.txt

# Aarch64
ARM64_ALIGNED     := $(BIN)_aarch64_aligned
ARM64_VANILLA     := $(BIN)_aarch64_vanilla
ARM64_MAP         := $(BIN)_aarch64_map.txt
ARM64_LD_SCRIPT   := aligned_linker_script_arm.x

###############################################################################
#                                 Recipes                                     #
###############################################################################

aligned-x86-64: $(X86_64_ALIGNED)
vanilla-x86-64: $(X86_64_VANILLA)
obj-x86-64:  	$(X86_64_OBJ)

######################################################

all: call_leaf.out call_leaf.s

######################################################

call_leaf.out: call_leaf.c
	clang $(CFLAGS) -g -S -emit-llvm call_leaf.c -o call_leaf_debug.ll # 2 flags for ffunction-sections fdata-sections
	opt $(OPT_FLAGS) -S call_leaf_debug.ll -o call_leaf_debug_opt.ll # 2 popcorn passes (if they work on opt)
	llc $(LLC_FLAGS) -filetype=obj call_leaf_debug_opt.ll -o call_leaf_2.o
	clang call_leaf_2.o -o call_leaf.out

######################################################

call_leaf.s: call_leaf.c
	clang $(CFLAGS) -S -emit-llvm call_leaf.c -o call_leaf.ll
	opt $(OPT_FLAGS) -S call_leaf.ll -o call_leaf_opt.ll
	llc $(LLC_FLAGS) call_leaf_opt.ll -o call_leaf$(subst =,_,$(OPT_FLAGS))$(subst =,_,$(LLC_FLAGS)).s

######################################################

$(X86_64_OBJ): $(SRC)
	clang $(CFLAGS) -g -S -emit-llvm $^ -o $(BIN)_debug.ll # 2 flags for ffunction-sections fdata-sections
	opt $(OPT_FLAGS) -S $(BIN)_debug.ll -o $(BIN)_debug_opt.ll # 2 popcorn passes (if they work on opt)
	llc $(LLC_FLAGS) -filetype=obj $(BIN)_debug_opt.ll -o $@

$(X86_64_VANILLA): $(X86_64_OBJ)
	@echo " [LD] $@ (vanilla)"
	@$(LD) -o $@ $(X86_64_OBJ) $(LDFLAGS) -Map $(X86_64_MAP)

$(X86_64_LD_SCRIPT): $(X86_64_VANILLA) $(ARM_64_VANILLA)
	@echo " [ALIGN] $@"
	@$(ALIGN) --compiler-inst $(POPCORN) \
		--x86-bin $(X86_64_VANILLA) --arm-bin $(ARM64_VANILLA) \
		--x86-map $(X86_64_MAP) --arm-map $(ARM64_MAP) \
		--output-x86-ls $(X86_64_LD_SCRIPT)	--output-arm-ls $(ARM64_LD_SCRIPT)

$(X86_64_ALIGNED): $(X86_64_LD_SCRIPT)
	@echo " [LD] $@ (aligned)"
	@$(LD) -o $@ $(X86_64_OBJ) $(LDFLAGS) $(X86_64_LDFLAGS) \
		-Map $(X86_64_ALIGNED_MAP) -T $<

clean:
	rm *.o *.ll *.out
