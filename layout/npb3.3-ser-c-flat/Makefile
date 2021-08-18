
all:
	for W in bt cg dc ep ft is lu mg sp ua; do \
		make -C $$W; \
	done

asm:
	for W in bt cg dc ep ft is lu mg sp ua; do \
		make -C $$W asm; \
	done

init:
	for W in bt cg dc ep ft is lu mg sp ua; do \
		make -C $$W init; \
	done

json:
	for W in bt cg dc ep ft is lu mg sp ua; do \
		make -C $$W json; \
	done

.PHONY: asm init json clean
clean:
	for W in bt cg dc ep ft is lu mg sp ua; do \
		make -C $$W clean; \
		rm -f $$W/npbparams.h; \
	done

.PHONY: S A B
S: clean
	./setclass.sh S
A: clean
	./setclass.sh A
B: clean
	./setclass.sh B

.PHONY: help
help:
	@echo "make {all | asm | init | json | S | A | B | clean}"
