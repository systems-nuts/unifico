TEST_SUITE := bubble-sort call-leaf factorial long-int-slot fp-args fp-spill-weight fp-stack-slot int-loop
TEST_SUITE += int-loop-accumulate many-add-mul read-write-global-array spill-weight-short spill-weight
TEST_SUITE += csr-example lsr-simple global-const global-fp-mul fp-loop-simple fp-loop
TEST_SUITE += char-arg create-seq c-print-results-1 c-print-results-call is-1 is-2 is-3 is-4 is-5

.PHONY: clean

all:
	for W in $(TEST_SUITE); do \
		make -C $$W; \
	done

test:
	for W in $(TEST_SUITE); do \
		(make -C $$W stackmaps-check) || exit 1; \
	done

clean:
	for W in $(TEST_SUITE); do \
		make -C $$W clean; \
	done

