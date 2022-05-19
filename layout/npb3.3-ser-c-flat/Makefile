BENCHMARKS ?= bt cg dc ep ft is lu mg sp ua

.DEFAULT_GOAL: all

.PHONY: all asm init json clean
all asm init json clean:
	$(foreach BMK,$(BENCHMARKS), $(if $(filter all, $@), make -C $(BMK), make -C $(BMK) $@))
	$(foreach BMK,$(BENCHMARKS), $(if $(filter clean, $@), rm -f $(BMK)/npbparams.h))

.PHONY: S A B C
S A B C: clean
	./setclass.sh $@

.PHONY: help
help:
	@echo "make {all | asm | init | json | S | A | B | C | clean}"
