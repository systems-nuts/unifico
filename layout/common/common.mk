###############################################################################
# FIXME's
###############################################################################
POPCORN 	   ?= /usr/local/popcorn

LLVM_TOOLCHAIN ?= ~/llvm-9/toolchain/bin

PYTHON ?= python3.9

# Lib musl directories per architecture
MUSL_TOOLCHAIN 	?= ~/musl-toolchains/llvm-9
ARM64_MUSL  	?= $(MUSL_TOOLCHAIN)/aarch64
X86_64_MUSL		?= $(MUSL_TOOLCHAIN)/x86-64

# Directory of libgcc & libgcc_eh for aarch64 compiler
ARM64_LIBGCC   ?= $(shell dirname \
	                $(shell aarch64-linux-gnu-gcc -print-libgcc-file-name))

# For llvm-mca tool TODO
MCA 			?= ~/llvm_13/toolchain/bin/llvm-mca
ARM64_CPU   	?= thunderx2t99
X86_64_CPU		?= btver2
MCA_RESULT_DIR 	?= ../mca-results/reg-pressure-O0

###############################################################################
# LLVM Tools and Flags
###############################################################################
CC  	:= $(LLVM_TOOLCHAIN)/clang
OPT 	:= $(LLVM_TOOLCHAIN)/opt
LLC 	:= $(LLVM_TOOLCHAIN)/llc
OBJDUMP	:= $(LLVM_TOOLCHAIN)/llvm-objdump

CFLAGS 		:= -Xclang -disable-O0-optnone -mno-red-zone -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer
CFLAGS 		+= -O1 -Wall -nostdinc
HET_CFLAGS 	:= $(CFLAGS) #-fno-common -ftls-model=initial-exec
OPT_FLAGS 	:= -name-string-literals -static-var-sections
LLC_FLAGS 	:= -function-sections -data-sections
LLC_FLAGS 	+= -relocation-model=pic --trap-unreachable -optimize-regalloc -fast-isel=false -disable-machine-cse

IR := $(SRC:.c=.ll)
IR_NODBG := $(SRC:.c=_nodbg.ll)

###############################################################################
# Linker and Flags
###############################################################################
LD       := $(POPCORN)/bin/x86_64-popcorn-linux-gnu-ld.gold
ARM64_LD := $(POPCORN)/bin/aarch64-popcorn-linux-gnu-ld.gold
#LD       := ~/musl-cross-make/output/x86_64-linux-musl/bin/ld
#ARM64_LD := ~/musl-cross-make/output/aarch64-linux-musl/bin/ld

LDFLAGS := -z noexecstack -z relro --hash-style=gnu --build-id -static
LIBS    := /lib/crt1.o \
           /lib/libc.a \
           /lib/libm.a

LIBGCC := --start-group -lgcc -lgcc_eh --end-group

###############################################################################
# Alignment
###############################################################################
ALIGN 					:= $(POPCORN)/bin/pyalign
ALIGN_CHECK 			:= $(POPCORN)/bin/check-align.py
CALLSITE_ALIGN			:= /home/nikos/phd/unified_abi/layout/callsites/callsite_align.py
CALLSITE_ALIGN_CHECK	:= /home/nikos/phd/unified_abi/layout/callsites/check_callsite_align.py

###############################################################################
# X86-64
###############################################################################
X86_64_POPCORN     := $(POPCORN)/x86_64
X86_64_BUILD       := build_x86-64
X86_64_ALIGNED     := $(BIN)_x86_64_aligned.out
X86_64_UNALIGNED   := $(BIN)_x86_64_unaligned.out
X86_64_INIT        := $(BIN)_x86_64_init.out
X86_64_OBJ_INIT    := $(SRC:.c=_x86_64_init.o) # Initial object files
X86_64_OBJ         := $(SRC:.c=_x86_64.o) # With callsite alignment
X86_64_ASM         := $(SRC:.c=_x86_64.s)
X86_64_MAP         := $(X86_64_BUILD)/map.txt
X86_64_LD_SCRIPT   := $(X86_64_BUILD)/aligned_linker_script_x86.x
X86_64_ALIGNED_MAP := $(X86_64_BUILD)/aligned_map.txt
X86_64_JSON        := $(SRC:.c=_x86_64.json)
X86_64_JSON_DIR    := $(MCA_RESULT_DIR)/x86-64/$(BIN)

X86_64_TARGET  := x86_64-linux-gnu
X86_64_INC     := -isystem $(X86_64_MUSL)/include # FIXME
X86_64_LDFLAGS := -m elf_x86_64 -L$(X86_64_MUSL)/lib \
                  $(addprefix $(X86_64_MUSL),$(LIBS)) \
                  --start-group --end-group

###############################################################################
# Aarch64
###############################################################################
ARM64_POPCORN 	  := $(POPCORN)/aarch64
ARM64_BUILD       := build_aarch64
ARM64_ALIGNED     := $(BIN)_aarch64_aligned.out
ARM64_UNALIGNED   := $(BIN)_aarch64_unaligned.out
ARM64_INIT        := $(BIN)_aarch64_init.out
ARM64_OBJ_INIT    := $(SRC:.c=_aarch64_init.o) # Initial object files
ARM64_OBJ         := $(SRC:.c=_aarch64.o) # With callsite alignment
ARM64_ASM         := $(SRC:.c=_aarch64.s)
ARM64_MAP         := $(ARM64_BUILD)/map.txt
ARM64_LD_SCRIPT   := $(ARM64_BUILD)/aligned_linker_script_arm.x
ARM64_ALIGNED_MAP := $(ARM64_BUILD)/aligned_map.txt
ARM64_JSON        := $(SRC:.c=_aarch64.json)
ARM64_JSON_DIR    := $(MCA_RESULT_DIR)/aarch64/$(BIN)

ARM64_TARGET  := aarch64-linux-gnu
ARM64_INC     := -isystem $(ARM64_MUSL)/include
ARM64_LDFLAGS := -m aarch64linux -L$(ARM64_MUSL)/lib -L$(ARM64_LIBGCC) \
	                 $(addprefix $(ARM64_MUSL),$(LIBS)) $(LIBGCC)

###############################################################################
#                                 Recipes                                     #
###############################################################################

all: aligned

ir: $(IR)
asm: asm-x86-64 asm-aarch64
json: json-x86-64 json-aarch64

# Small hack to cancel the implicit assembler rule
%.o : %.s

aligned: aligned-x86-64 aligned-aarch64
unaligned: unaligned-x86-64 unaligned-aarch64
init: init-x86-64 init-aarch64

aligned-x86-64: $(X86_64_ALIGNED)
unaligned-x86-64: $(X86_64_UNALIGNED)
init-x86-64: $(X86_64_INIT)
obj-x86-64-init: $(X86_64_OBJ_INIT)
obj-x86-64: $(X86_64_OBJ)
asm-x86-64: $(X86_64_ASM)
json-x86-64: $(X86_64_JSON)

aligned-aarch64: $(ARM64_ALIGNED)
unaligned-aarch64: $(ARM64_UNALIGNED)
init-aarch64: $(ARM64_INIT)
obj-aarch64-init: $(ARM64_OBJ_INIT)
obj-aarch64: $(ARM64_OBJ)
asm-aarch64: $(ARM64_ASM)
json-aarch64: $(ARM64_JSON)

.PRECIOUS: $(BIN)_cs_align.json

##########
# Common #
##########

%.ll: %.c
	@echo " [IR] $@"
	$(CC) $(HET_CFLAGS) -ggdb3 -S -emit-llvm $(ARM64_INC) -o $@ $<
	# Remove the x86-64-related information
	sed -e "s/\"target-cpu\"\=\"x86-64\"\ \"target-features\"\=\"+cx8,+fxsr,+mmx,+sse,+sse2,+x87\"//g" -i $@
	# Make directories
	mkdir -p $(X86_64_BUILD) $(ARM64_BUILD)

%_opt.ll: %.ll
	@echo " [OPT] $@"
	$(OPT) $(OPT_FLAGS) -S -o $@ $<

%_nodbg.ll: %.c
	@echo " [IR NO DEBUG] $@"
	$(CC) $(HET_CFLAGS) -S -emit-llvm $(ARM64_INC) -o $@ $<
	# Remove the x86-64-related information
	sed -e "s/\"target-cpu\"\=\"x86-64\"\ \"target-features\"\=\"+cx8,+fxsr,+mmx,+sse,+sse2,+x87\"//g" -i $@
	# Make directories
	mkdir -p $(X86_64_BUILD) $(ARM64_BUILD) $(X86_64_JSON_DIR) $(ARM64_JSON_DIR)

%_opt_nodbg.ll: %_nodbg.ll
	@echo " [OPT NO DEBUG] $@"
	$(OPT) $(OPT_FLAGS) -S -o $@ $<

%_cs_align.json: %_x86_64_init.o %_aarch64_init.o # TODO improve objdump output names
	@echo " [CALLSITE ALIGN] $@"
	$(OBJDUMP) -d $< >$(X86_64_BUILD)/$*_x86_64_init.objdump
	$(OBJDUMP) -d $(word 2,$^) >$(ARM64_BUILD)/$*_aarch64_init.objdump 
	$(PYTHON) $(CALLSITE_ALIGN) $(ARM64_BUILD)/$*_aarch64_init.objdump $(X86_64_BUILD)/$*_x86_64_init.objdump >$@

###########
# AArch64 #
###########

%_aarch64.s: %_opt_nodbg.ll
	@echo " [LLC ASSEMBLY] $@"
	$(LLC) $(LLC_FLAGS) -march=aarch64 -o $(ARM64_BUILD)/$(<:_opt_nodbg.ll=_aarch64.s) $<

%_aarch64.json: %_aarch64.s
	@echo " [LLVM-MCA] $@"
	#$(MCA) -march=aarch64 -mcpu=$(ARM64_CPU) -json -o $(ARM64_JSON_DIR)/$(<:.s=.json) $(ARM64_BUILD)/$<
	$(MCA) -march=aarch64 -mcpu=$(ARM64_CPU) -register-file-stats -o $(ARM64_JSON_DIR)/$(<:.s=.json) $(ARM64_BUILD)/$<

%_aarch64_init.o: %_opt.ll 
	@echo " [LLC] $@"
	$(LLC) $(LLC_FLAGS) -march=aarch64 -filetype=obj -o $(<:_opt.ll=_aarch64_init.o) $<

%_aarch64.o: %_cs_align.json %_opt.ll
	@echo " [LLC WITH CALLSITE ALIGNMENT] $@"
	$(LLC) $(LLC_FLAGS) -march=aarch64 -filetype=obj -callsite-padding=$< -o $@ $(word 2,$^)

$(ARM64_INIT): $(ARM64_OBJ_INIT)
	@echo " [LD] $@"
	$(LD) -o $@ $^ $(LDFLAGS) $(ARM64_LDFLAGS) -Map $(ARM64_MAP)
	sshpass -f "/home/nikos/docs/pass.txt" scp $@ nikos@sole:`pwd`

$(ARM64_UNALIGNED): $(ARM64_OBJ)
	@echo " [LD] $@"
	$(LD) -o $@ $^ $(LDFLAGS) $(ARM64_LDFLAGS) -Map $(ARM64_MAP)

$(ARM64_LD_SCRIPT): $(X86_64_LD_SCRIPT)
	@echo " [ALIGN] $@"

$(ARM64_ALIGNED): $(ARM64_LD_SCRIPT)
	@echo " [LD] $@"
	$(LD) -o $@ $(ARM64_OBJ) $(LDFLAGS) $(ARM64_LDFLAGS) -Map $(ARM64_ALIGNED_MAP) -T $<
	sshpass -f "/home/nikos/docs/pass.txt" scp $@ nikos@sole:`pwd`

##########
# x86-64 #
##########

%_x86_64.s: %_opt_nodbg.ll
	@echo " [LLC ASSEMBLY] $@"
	$(LLC) $(LLC_FLAGS) -march=x86-64 --x86-asm-syntax=intel -o $(X86_64_BUILD)/$(<:_opt_nodbg.ll=_x86_64.s) $<

%_x86_64.json: %_x86_64.s
	@echo " [LLVM-MCA] $@"
	#$(MCA) -march=x86-64 -mcpu=$(X86_64_CPU) -json -o $(X86_64_JSON_DIR)/$(<:.s=.json) $(X86_64_BUILD)/$<
	$(MCA) -march=x86-64 -mcpu=$(X86_64_CPU) -register-file-stats -o $(X86_64_JSON_DIR)/$(<:.s=.json) $(X86_64_BUILD)/$<

%_x86_64_init.o: %_opt.ll
	@echo " [LLC] $@"
	$(LLC) $(LLC_FLAGS) -march=x86-64 -filetype=obj -o $(<:_opt.ll=_x86_64_init.o) $<

%_x86_64.o: %_cs_align.json %_opt.ll %_aarch64.o
	@echo " [LLC WITH CALLSITE ALIGNMENT] $@"
	$(LLC) $(LLC_FLAGS) -march=x86-64 -filetype=obj -callsite-padding=$< -o $@ $(word 2,$^)
	@echo " [CHECK CALLSITE ALIGNMENT] $@ $(word 3,$^)"
	$(OBJDUMP) -d $@ >$(X86_64_BUILD)/$*_x86_64.objdump
	$(OBJDUMP) -d $(word 3,$^) >$(ARM64_BUILD)/$*_aarch64.objdump 
	$(PYTHON) $(CALLSITE_ALIGN_CHECK) $(ARM64_BUILD)/$*_aarch64.objdump $(X86_64_BUILD)/$*_x86_64.objdump

$(X86_64_INIT): $(X86_64_OBJ_INIT)
	@echo " [LD] $@"
	$(LD) -o $@ $^ $(LDFLAGS) $(X86_64_LDFLAGS) -Map $(X86_64_MAP)

$(X86_64_UNALIGNED): $(X86_64_OBJ)
	@echo " [LD] $@"
	$(LD) -o $@ $^ $(LDFLAGS) $(X86_64_LDFLAGS) -Map $(X86_64_MAP)

$(X86_64_LD_SCRIPT): $(ARM64_UNALIGNED) $(X86_64_UNALIGNED)
	@echo " [ALIGN] $@"
	$(ALIGN) --compiler-inst $(POPCORN) \
		--x86-bin $(X86_64_UNALIGNED) --arm-bin $(ARM64_UNALIGNED) \
		--x86-map $(X86_64_MAP) --arm-map $(ARM64_MAP) \
		--output-x86-ls $(X86_64_LD_SCRIPT) --output-arm-ls $(ARM64_LD_SCRIPT)

$(X86_64_ALIGNED): $(X86_64_LD_SCRIPT)
	@echo " [LD] $@"
	$(LD) -o $@ $(X86_64_OBJ) $(LDFLAGS) $(X86_64_LDFLAGS) -Map $(X86_64_ALIGNED_MAP) -T $<

check_un: $(ARM64_ALIGNED) $(X86_64_ALIGNED)
	@echo " [CHECK] Checking unalignment for $^"
	$(PYTHON) $(ALIGN_CHECK) $(ARM64_UNALIGNED) $(X86_64_UNALIGNED)

check: $(ARM64_ALIGNED) $(X86_64_ALIGNED)
	@echo " [CHECK] Checking alignment for $^"
	$(PYTHON) $(ALIGN_CHECK) $(ARM64_ALIGNED) $(X86_64_ALIGNED)

clean:
	@echo " [CLEAN] $(ARM64_ALIGNED) $(ARM64_BUILD) $(ARM64_JSON_DIR) $(X86_64_ALIGNED) $(X86_64_BUILD) $(X86_64_JSON_DIR) \
		$(X86_64_SD_BUILD) $(X86_64_LD_SCRIPT) $(ARM64_LD_SCRIPT) *.ll *.s *.json *.o *.out"
	@rm -rf $(ARM64_ALIGNED) $(ARM64_BUILD) $(ARM64_JSON_DIR) $(X86_64_ALIGNED) $(X86_64_BUILD) $(X86_64_JSON_DIR) \
		$(X86_64_SD_BUILD) $(X86_64_LD_SCRIPT) $(ARM64_LD_SCRIPT) *.ll *.s *json *.o *.out

.PHONY: all check clean \
        aligned aligned-aarch64 aligned-x86-64 \
        unaligned unaligned-aarch64 unaligned-x86-64 \
        init init-aarch64 init-x86-64
