
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
OPT_FLAGS := -O0
LLC_FLAGS := -O0
LDFLAGS := -z noexecstack -z relro --hash-style=gnu --build-id 
LIBS    := /lib/crt1.o \
	/lib/libc.a \
	/lib/libelf.a \
	/lib/libpthread.a \
	/lib/libc.a \
	/lib/libm.a

X86_64_LDFLAGS := -m elf_x86_64 -L$(X86_64_POPCORN)/lib \
                  $(addprefix $(X86_64_POPCORN),$(LIBS)) \
                  --start-group --end-group
ARM64_LDFLAGS := -m aarch64linux -L$(ARM64_POPCORN)/lib -L$(ARM64_LIBGCC) \
	                 $(addprefix $(ARM64_POPCORN),$(LIBS)) $(LIBGCC)

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

call_leaf_x86.ll: call_leaf.c
	clang $(CFLAGS) -g -S -emit-llvm -ffunction-sections -fdata-sections call_leaf.c -o call_leaf_x86.ll 

call_leaf_x86_opt.ll: call_leaf_x86.ll
	opt $(OPT_FLAGS) -S call_leaf_x86.ll -o call_leaf_x86_opt.ll 

call_leaf_x86.o: call_leaf_x86_opt.ll
	llc $(LLC_FLAGS) -filetype=obj call_leaf_x86_opt.ll -o call_leaf_x86.o

call_leaf_x86_unaligned.out: call_leaf_x86.o
	$(LD) -o $@ $^ $(LDFLAGS) $(X86_64_LDFLAGS) -Map $(X86_64_MAP)

call_leaf_aarch64.o: call_leaf_x86_opt.ll
	llc $(LLC_FLAGS) -march=aarch64 -filetype=obj call_leaf_x86_opt.ll -o call_leaf_aarch64.o

call_leaf_aarch64_unaligned.out: call_leaf_aarch64.o
	$(LD) -o $@ $^ $(LDFLAGS) $(ARM64_LDFLAGS) -Map $(ARM64_MAP)

linker_scripts: call_leaf_x86_unaligned.out call_leaf_aarch64_unaligned.out
	$(ALIGN) --compiler-inst /usr/local/popcorn --x86-bin call_leaf_x86_unaligned.out --arm-bin call_leaf_aarch64_unaligned.out --x86-map build_x86-64/map.txt --arm-map build_aarch64/map.txt --output-x86-ls build_x86-64/aligned_linker_script_x86.x --output-arm-ls build_aarch64/aligned_linker_script_arm.x

######################################################

call_leaf.s: call_leaf.c
	clang $(CFLAGS) -S -emit-llvm call_leaf.c -o call_leaf.ll
	opt $(OPT_FLAGS) -S call_leaf.ll -o call_leaf_opt.ll
	llc $(LLC_FLAGS) call_leaf_opt.ll -o call_leaf$(subst =,_,$(OPT_FLAGS))$(subst =,_,$(LLC_FLAGS)).s

######################################################

clean:
	rm *.o *.ll *.out
