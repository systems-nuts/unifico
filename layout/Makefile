TEST_SUITE := bubble-sort call-leaf factorial long-int-slot fp-args fp-spill-weight fp-stack-slot int-loop
TEST_SUITE += int-loop-accumulate many-add-mul read-write-global-array spill-weight-short spill-weight

.PHONY: clean

all:
	for W in $(TEST_SUITE); do \
		make -C $$W; \
	done

test:
	for W in $(TEST_SUITE); do \
		make -C $$W stackmaps-check; \
	done

clean:
	for W in $(TEST_SUITE); do \
		make -C $$W clean; \
	done

