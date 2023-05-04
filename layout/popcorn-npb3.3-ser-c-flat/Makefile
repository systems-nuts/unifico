
all:
	for W in bt cg dc ep ft is lu mg sp ua; do \
		make -j10 -C $$W aligned; \
	done

.PHONY: clean
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
	@echo "make {all | S | A | B | clean}"
