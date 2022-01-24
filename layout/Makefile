TEST_SUITE ?= bubble_sort call_leaf fact global

.PHONY: clean

all:
	for W in $(TEST_SUITE); do \
		make -C $$W; \
	done

clean:
	for W in $(TEST_SUITE); do \
		make -C $$W clean; \
	done

