#

MKFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
MKFILE_DIR := $(dir $(MKFILE_PATH))

DEFS_MKFILE ?= $(MKFILE_DIR)/$(shell hostname).defs.mk

$(if $(shell test -s $(DEFS_MKFILE)), $(error "file $(DEFS_MKFILE) does not exist"),)

include $(DEFS_MKFILE)

SSHPASS_IGNORE ?= @- # silent and ignored by default - override with DEFS_MAKEFILE
QUIET = @

###############################################################################
# LLVM Tools and Flags
###############################################################################
CC		:= $(LLVM_TOOLCHAIN)/clang
OPT		:= $(LLVM_TOOLCHAIN)/opt
LLC		:= $(LLVM_TOOLCHAIN)/llc
OBJDUMP	:= $(LLVM_TOOLCHAIN)/llvm-objdump
X86_64_OBJDUMP := x86_64-linux-gnu-objdump

OPT_LEVEL ?= -O0
override CFLAGS += $(OPT_LEVEL) -Wall
override CFLAGS += -Xclang -disable-O0-optnone -mno-red-zone -fno-omit-frame-pointer -mno-omit-leaf-frame-pointer

ifndef UNMODIFIED_LLVM
override CFLAGS += -mllvm -align-bytes-to-four

override OPT_FLAGS	+= -name-string-literals -static-var-sections -live-values -insert-stackmaps

override LLC_FLAGS	+= -function-sections -data-sections
override LLC_FLAGS	+= -relocation-model=pic --trap-unreachable -optimize-regalloc -fast-isel=false -disable-machine-cse

ifndef EXPERIMENT_MODE
# Callsite-related
override LLC_FLAGS  += -disable-block-align --mc-relax-all
# Custom
override LLC_FLAGS  += -disable-x86-frame-obj-order -aarch64-csr-alignment=8 -align-bytes-to-four -reg-scavenging-slot -enable-misched=false

override LLC_FLAGS_ARM64 += -mattr=-disable-hoist-in-lowering,+disable-fp-imm-materialize,-avoid-f128,+avoid-wide-mul-add,+copy-wzr-temp
override LLC_FLAGS_X86 += -mattr=+aarch64-sized-imm,-multiply-with-imm,-non-zero-imm-to-mem,+force-vector-mem-op,+aarch64-constant-cost-model,+simple-reg-offset-addr,+avoid-opt-mul-1 -no-x86-call-frame-opt -x86-enable-simplify-cfg -enable-lea32
endif
endif

LLC_PASSES_TO_DEBUG	?= isel regalloc stackmaps stacktransform

HET_CFLAGS	:= $(CFLAGS) #-fno-common -ftls-model=initial-exec

IR := $(SRC:.c=.ll)
IR_NODBG := $(SRC:.c=_nodbg.ll)

# Dump flag info in JSON-like fields
$(info {"CFLAGS": "${CFLAGS}",)
$(info "OPT_FLAGS": "${OPT_FLAGS}",)
$(info "LLC_FLAGS": "${LLC_FLAGS}",)
$(info "LLC_FLAGS_ARM64": "${LLC_FLAGS_ARM64}",)
$(info "LLC_FLAGS_X86": "${LLC_FLAGS_X86}"})

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
ALIGN	:= $(POPCORN)/bin/pyalign
ALIGN_CHECK	:= $(POPCORN)/bin/check-align.py
CALLSITE_ALIGN	:= $(PROJECT_DIR)/layout/callsites/align/callsite_align.py
CALLSITE_ALIGN_CHECK	:= $(PROJECT_DIR)/layout/callsites/check_callsite_align.py

###############################################################################
# Stackmaps
###############################################################################
STACKMAP_DUMP			:= $(PROJECT_DIR)/stack-metadata/dump-llvm-stackmap
STACKMAP_CHECK			:= $(PROJECT_DIR)/stack-metadata/check-stackmaps
STACKMAP_SRC_DIR	:= $(PROJECT_DIR)/stack-metadata/

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
ARM64_POPCORN			:= $(POPCORN)/aarch64
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
stackmaps-dump: stackmaps-dump-x86-64 stackmaps-dump-aarch64

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
.PRECIOUS: $(BIN)_opt.ll

#############
# Stackmaps #
#############

stackmaps-dump-aarch64: $(ARM64_ALIGNED)
	@echo " [STACKMAP DUMP] $^"
	$(QUIET) { \
		if [ -z ${TARGET_FUNC} ] && [ -z ${TARGET_CALLSITE} ]; then \
		$(STACKMAP_DUMP) -f $(ARM64_ALIGNED); \
		elif [ -z ${TARGET_CALLSITE} ]; then \
		$(STACKMAP_DUMP) -f $(ARM64_ALIGNED) -n $(TARGET_FUNC); \
		else \
		$(STACKMAP_DUMP) -f $(ARM64_ALIGNED) -n $(TARGET_FUNC) -c $(TARGET_CALLSITE); \
		fi \
		}

stackmaps-dump-x86-64: $(X86_64_ALIGNED)
	@echo " [STACKMAP DUMP] $^"
	$(QUIET) { \
		if [ -z ${TARGET_FUNC} ] && [ -z ${TARGET_CALLSITE} ]; then \
		$(STACKMAP_DUMP) -f $(X86_64_ALIGNED); \
		elif [ -z ${TARGET_CALLSITE} ]; then \
		$(STACKMAP_DUMP) -f $(X86_64_ALIGNED) -n $(TARGET_FUNC); \
		else \
		$(STACKMAP_DUMP) -f $(X86_64_ALIGNED) -n $(TARGET_FUNC) -c $(TARGET_CALLSITE); \
		fi \
		}

stackmaps-check: $(ARM64_ALIGNED) $(X86_64_ALIGNED)
	@echo " [STACKMAPS CHECK] Checking stackmaps for $^"
	$(QUIET) make -C $(STACKMAP_SRC_DIR)
	$(QUIET) { \
		if [ -z ${TARGET_FUNC} ]; then \
		$(STACKMAP_CHECK) -a $(ARM64_ALIGNED) -x $(X86_64_ALIGNED); \
		else \
		$(STACKMAP_CHECK) -a $(ARM64_ALIGNED) -x $(X86_64_ALIGNED) -f $(TARGET_FUNC); \
		fi \
		}


##########
# Common #
##########

%.ll: %.c src_changed
	@echo " [IR] $@"
	$(QUIET) $(CC) $(HET_CFLAGS) -I $(INC_DIR) -ggdb3 -S -emit-llvm $(ARM64_INC) -o $@ $<
	$(QUIET) # Remove the x86-64-related information
	$(QUIET) sed -e "s/\"target-cpu\"\=\"x86-64\"\ \"target-features\"\=\"+cx8,+fxsr,+mmx,+sse,+sse2,+x87\"//g" -i $@
	$(QUIET) # Make directories
	$(QUIET) mkdir -p $(X86_64_BUILD) $(ARM64_BUILD)

%_opt.ll: %.ll
	@echo " [OPT] $@"
	$(QUIET) $(OPT) $(OPT_FLAGS) -S -o $@ $<

%_nodbg.ll: %.c
	@echo " [IR NO DEBUG] $@"
	$(QUIET) $(CC) $(HET_CFLAGS) -I $(INC_DIR) -S -emit-llvm $(ARM64_INC) -o $@ $<
	$(QUIET) # Remove the x86-64-related information
	$(QUIET) sed -e "s/\"target-cpu\"\=\"x86-64\"\ \"target-features\"\=\"+cx8,+fxsr,+mmx,+sse,+sse2,+x87\"//g" -i $@
	$(QUIET) # Make directories
	$(QUIET) mkdir -p $(X86_64_BUILD) $(ARM64_BUILD) $(X86_64_JSON_DIR) $(ARM64_JSON_DIR)

%_opt_nodbg.ll: %_nodbg.ll
	@echo " [OPT NO DEBUG] $@"
	$(QUIET) $(OPT) $(OPT_FLAGS) -S -o $@ $<

%_cs_align.json: %_x86_64_init.o %_aarch64_init.o # TODO improve objdump output names
	@echo " [CALLSITE ALIGN] $@"
	$(QUIET) $(X86_64_OBJDUMP) -d -M intel $< >$(X86_64_BUILD)/$*_x86_64_init.objdump
	$(QUIET) $(OBJDUMP) -d --print-imm-hex $(word 2,$^) >$(ARM64_BUILD)/$*_aarch64_init.objdump
	$(QUIET) $(CALLSITE_ALIGN) $(ARM64_BUILD)/$*_aarch64_init.objdump $(X86_64_BUILD)/$*_x86_64_init.objdump >$@

src_changed: *.c
	@echo " [SOURCE FILES CHANGED]"
	echo $?
	touch $@
	$(QUIET) { \
		if [ -z ${SSHPASS_IGNORE} ]; then \
			$(SSHPASS_IGNORE)sshpass -f "/home/nikos/docs/pass.txt" scp $^ nikos@sole:`pwd`; \
		fi \
		}

###########
# AArch64 #
###########

%_aarch64.s: %_opt_nodbg.ll
	@echo " [LLC ASSEMBLY] $@"
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_ARM64) -march=aarch64 -o $(ARM64_BUILD)/$(<:_opt_nodbg.ll=_aarch64.s) $<

%_aarch64.json: %_aarch64.s
	@echo " [LLVM-MCA] $@"
	$(QUIET) #$(MCA) -march=aarch64 -mcpu=$(ARM64_CPU) -json -o $(ARM64_JSON_DIR)/$(<:.s=.json) $(ARM64_BUILD)/$<
	$(QUIET) $(MCA) -march=aarch64 -mcpu=$(ARM64_CPU) -register-file-stats -o $(ARM64_JSON_DIR)/$(<:.s=.json) $(ARM64_BUILD)/$<

%_aarch64_init.o: %_opt.ll
	@echo " [LLC] $@"
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_ARM64) -march=aarch64 -filetype=obj -o $(<:_opt.ll=_aarch64_init.o) $<
	$(QUIET){ \
		for PASS in $(LLC_PASSES_TO_DEBUG); do \
		$(LLC) $(LLC_FLAGS) $(LLC_FLAGS_ARM64) -march=aarch64 -filetype=obj -o  $(<:_opt.ll=_aarch64_init.o) $< -debug-only=$$PASS 2>$(ARM64_BUILD)/$*_$${PASS}_init.txt; \
		done \
		}


%_aarch64.o: %_cs_align.json %_opt.ll
	@echo " [LLC WITH CALLSITE ALIGNMENT] $@"
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_ARM64) -march=aarch64 -filetype=obj -callsite-padding=$< -o $@ $(word 2,$^)
	$(QUIET){ \
	for PASS in $(LLC_PASSES_TO_DEBUG); do \
		$(LLC) $(LLC_FLAGS) $(LLC_FLAGS_ARM64) -march=aarch64 -filetype=obj -callsite-padding=$< -o $@ $(word 2,$^) -debug-only=$$PASS 2>$(ARM64_BUILD)/$*_$$PASS.txt; \
		done \
		}

$(ARM64_INIT): $(ARM64_OBJ_INIT)
	@echo " [LD] $@"
	$(QUIET) $(LD) -o $@ $^ $(LDFLAGS) $(ARM64_LDFLAGS) -Map $(ARM64_MAP)
	$(QUIET) { \
		if [ -z ${SSHPASS_IGNORE} ]; then \
			$(SSHPASS_IGNORE)sshpass -f "/home/nikos/docs/pass.txt" scp $@ nikos@sole:`pwd`; \
		fi \
		}
	$(QUIET) $(OBJDUMP) -d -S --print-imm-hex $@ >aarch64_objdump.txt

$(ARM64_UNALIGNED): $(ARM64_OBJ)
	@echo " [LD] $@"
	$(QUIET) $(LD) -o $@ $^ $(LDFLAGS) $(ARM64_LDFLAGS) -Map $(ARM64_MAP)

$(ARM64_LD_SCRIPT): $(X86_64_LD_SCRIPT)
	@echo " [ALIGN] $@"

$(ARM64_ALIGNED): $(ARM64_LD_SCRIPT)
	@echo " [LD] $@"
	$(QUIET) $(LD) -o $@ $(ARM64_OBJ) $(LDFLAGS) $(ARM64_LDFLAGS) -Map $(ARM64_ALIGNED_MAP) -T $<
	$(QUIET) { \
		if [ -z ${SSHPASS_IGNORE} ]; then \
			$(SSHPASS_IGNORE)sshpass -f "/home/nikos/docs/pass.txt" scp $@ nikos@sole:`pwd`; \
		fi \
		}
	$(QUIET) $(OBJDUMP) -d -S --print-imm-hex $@ >aarch64_objdump.txt

##########
# x86-64 #
##########

%_x86_64.s: %_opt_nodbg.ll
	@echo " [LLC ASSEMBLY] $@"
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_X86) -march=x86-64 --x86-asm-syntax=intel -o $(X86_64_BUILD)/$(<:_opt_nodbg.ll=_x86_64.s) $<

%_x86_64.json: %_x86_64.s
	@echo " [LLVM-MCA] $@"
	$(QUIET) #$(MCA) -march=x86-64 -mcpu=$(X86_64_CPU) -json -o $(X86_64_JSON_DIR)/$(<:.s=.json) $(X86_64_BUILD)/$<
	$(QUIET) $(MCA) -march=x86-64 -mcpu=$(X86_64_CPU) -register-file-stats -o $(X86_64_JSON_DIR)/$(<:.s=.json) $(X86_64_BUILD)/$<

%_x86_64_init.o: %_opt.ll
	@echo " [LLC] $@"
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_X86) -march=x86-64 -filetype=obj -o $(<:_opt.ll=_x86_64_init.o) $<
	$(QUIET){ \
		for PASS in $(LLC_PASSES_TO_DEBUG); do \
		$(LLC) $(LLC_FLAGS) $(LLC_FLAGS_X86) -march=x86-64 -filetype=obj -o $(<:_opt.ll=_x86_64_init.o) $< -debug-only=$$PASS 2>$(X86_64_BUILD)/$*_$${PASS}_init.txt; \
		done \
		}


%_x86_64.o: %_cs_align.json %_opt.ll %_aarch64.o
	@echo " [LLC WITH CALLSITE ALIGNMENT] $@"
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_X86) -march=x86-64 -filetype=obj -callsite-padding=$< -o $@ $(word 2,$^)
	@echo " [CHECK CALLSITE ALIGNMENT] $@ $(word 3,$^)"
	$(QUIET) $(X86_64_OBJDUMP) -d -M intel $@ >$(X86_64_BUILD)/$*_x86_64.objdump
	$(QUIET) $(OBJDUMP) -d --print-imm-hex $(word 3,$^) >$(ARM64_BUILD)/$*_aarch64.objdump
	$(QUIET){ \
	for PASS in $(LLC_PASSES_TO_DEBUG); do \
		$(LLC) $(LLC_FLAGS) $(LLC_FLAGS_X86) -march=x86-64 -filetype=obj -callsite-padding=$< -o $@ $(word 2,$^) -debug-only=$$PASS 2>$(X86_64_BUILD)/$*_$$PASS.txt; \
		done \
		}
	$(QUIET) { \
		if [ -z ${EXPERIMENT_MODE} ]; then \
			$(CALLSITE_ALIGN_CHECK) $(ARM64_BUILD)/$*_aarch64.objdump $(X86_64_BUILD)/$*_x86_64.objdump; \
		fi \
		}

$(X86_64_INIT): $(X86_64_OBJ_INIT)
	@echo " [LD] $@"
	$(QUIET) $(LD) -o $@ $^ $(LDFLAGS) $(X86_64_LDFLAGS) -Map $(X86_64_MAP)
	$(QUIET) $(X86_64_OBJDUMP) -d -S -M intel $@ >x86_objdump.txt

$(X86_64_UNALIGNED): $(X86_64_OBJ)
	@echo " [LD] $@"
	$(QUIET) $(LD) -o $@ $^ $(LDFLAGS) $(X86_64_LDFLAGS) -Map $(X86_64_MAP)

$(X86_64_LD_SCRIPT): $(ARM64_UNALIGNED) $(X86_64_UNALIGNED)
	@echo " [ALIGN] $@"
	$(QUIET) $(ALIGN) --compiler-inst $(POPCORN) \
		--x86-bin $(X86_64_UNALIGNED) --arm-bin $(ARM64_UNALIGNED) \
		--x86-map $(X86_64_MAP) --arm-map $(ARM64_MAP) \
		--output-x86-ls $(X86_64_LD_SCRIPT) --output-arm-ls $(ARM64_LD_SCRIPT)

$(X86_64_ALIGNED): $(X86_64_LD_SCRIPT)
	@echo " [LD] $@"
	$(QUIET) $(LD) -o $@ $(X86_64_OBJ) $(LDFLAGS) $(X86_64_LDFLAGS) -Map $(X86_64_ALIGNED_MAP) -T $<
	$(QUIET) $(X86_64_OBJDUMP) -d -S -M intel $@ >x86_objdump.txt

check_un: $(ARM64_ALIGNED) $(X86_64_ALIGNED)
	@echo " [CHECK] Checking unalignment for $^"
	$(QUIET) $(ALIGN_CHECK) $(ARM64_UNALIGNED) $(X86_64_UNALIGNED)

check: $(ARM64_ALIGNED) $(X86_64_ALIGNED)
	@echo " [CHECK] Checking alignment for $^"
	$(QUIET) $(ALIGN_CHECK) $(ARM64_ALIGNED) $(X86_64_ALIGNED)

debug_pass_%: %_cs_align.json %_opt.ll %_aarch64.o
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_X86) -march=x86-64 -filetype=obj -callsite-padding=$< -o temp.o $(word 2,$^) -debug-only=$(PASS) 2>$(X86_64_BUILD)/$*_$(PASS).txt
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_ARM64) -march=aarch64 -filetype=obj -callsite-padding=$< -o temp.o $(word 2,$^) -debug-only=$(PASS) 2>$(ARM64_BUILD)/$*_$(PASS).txt

pass_structure_%: %_cs_align.json %_opt.ll %_aarch64.o
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_X86) -march=x86-64 -filetype=obj -callsite-padding=$< -o temp.o $(word 2,$^) -debug-pass=Structure 2>$(X86_64_BUILD)/$*_pass_structure.txt
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_ARM64) -march=aarch64 -filetype=obj -callsite-padding=$< -o temp.o $(word 2,$^) -debug-pass=Structure 2>$(ARM64_BUILD)/$*_pass_structure.txt

before_after_pass_%: %_cs_align.json %_opt.ll %_aarch64.o
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_X86) -march=x86-64 -filetype=obj -callsite-padding=$< -o temp.o $(word 2,$^) -print-before=$(PASS) 2>$(X86_64_BUILD)/$*_before_$(PASS).txt
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_X86) -march=x86-64 -filetype=obj -callsite-padding=$< -o temp.o $(word 2,$^) -print-after=$(PASS) 2>$(X86_64_BUILD)/$*_after_$(PASS).txt
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_ARM64) -march=aarch64 -filetype=obj -callsite-padding=$< -o temp.o $(word 2,$^) -print-before=$(PASS) 2>$(ARM64_BUILD)/$*_before_$(PASS).txt
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_ARM64) -march=aarch64 -filetype=obj -callsite-padding=$< -o temp.o $(word 2,$^) -print-after=$(PASS) 2>$(ARM64_BUILD)/$*_after_$(PASS).txt

init_before_after_pass_%: %_opt.ll
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_X86) -march=x86-64 -filetype=obj -o temp.o $< -print-before=$(PASS) 2>$(X86_64_BUILD)/$*_before_$(PASS).txt
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_X86) -march=x86-64 -filetype=obj -o temp.o $< -print-after=$(PASS) 2>$(X86_64_BUILD)/$*_after_$(PASS).txt
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_ARM64) -march=aarch64 -filetype=obj -o temp.o $< -print-before=$(PASS) 2>$(ARM64_BUILD)/$*_before_$(PASS).txt
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_ARM64) -march=aarch64 -filetype=obj -o temp.o $< -print-after=$(PASS) 2>$(ARM64_BUILD)/$*_after_$(PASS).txt

view_isel_dag_%: %_cs_align.json %_opt.ll %_aarch64.o
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_X86) -march=x86-64 -filetype=obj -callsite-padding=$< -o temp.o $(word 2,$^) -view-isel-dags -filter-view-dags=$(BASIC_BLOCK)
	$(QUIET) $(LLC) $(LLC_FLAGS) $(LLC_FLAGS_ARM64) -march=aarch64 -filetype=obj -callsite-padding=$< -o temp.o $(word 2,$^) -view-isel-dags -filter-view-dags=$(BASIC_BLOCK)

clean:
	@echo " [CLEAN] $(ARM64_ALIGNED) $(ARM64_BUILD) $(ARM64_JSON_DIR) $(X86_64_ALIGNED) $(X86_64_BUILD) $(X86_64_JSON_DIR) \
		$(X86_64_SD_BUILD) $(X86_64_LD_SCRIPT) $(ARM64_LD_SCRIPT) *.ll *.s *.json *.o *.out"
	@rm -rf $(ARM64_ALIGNED) $(ARM64_BUILD) $(ARM64_JSON_DIR) $(X86_64_ALIGNED) $(X86_64_BUILD) $(X86_64_JSON_DIR) \
		$(X86_64_SD_BUILD) $(X86_64_LD_SCRIPT) $(ARM64_LD_SCRIPT) *.ll *.s *json *.o *.out

.PHONY: all check clean \
	aligned aligned-aarch64 aligned-x86-64 \
	unaligned unaligned-aarch64 unaligned-x86-64 \
	init init-aarch64 init-x86-64 \
	stackmaps-dump stackmaps-check
