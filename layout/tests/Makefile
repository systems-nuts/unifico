TEST_SUITE := bubble-sort call-leaf factorial long-int-slot fp-args fp-spill-weight fp-stack-slot int-loop
TEST_SUITE += int-loop-accumulate many-add-mul read-write-global-array spill-weight-short spill-weight
TEST_SUITE += csr-example lsr-simple global-const global-fp-mul fp-loop-simple fp-loop
TEST_SUITE += char-arg create-seq c-print-results-1 c-print-results-call is-1 is-2 is-3 is-4 is-5 is-6 is-7
TEST_SUITE += cg-sparse-1 cg-sparse cg-sprnvc-1 cg-sprnvc-2 cg-sprnvc-4 cg-sprnvc-5 cg-makea-1 cg-makea-2 cg-makea-3 cg-makea-4 cg-main-1 cg-main-2 cg-main-3 cg-main-4 cg-main-5 cg-main
TEST_SUITE += ep-main-1 zero-constant-reuse ep-main-3 ep-main
TEST_SUITE += ft-verify ft-comp-init ft-fft3d-2 ft-fft3d-3 ft-appft-1 ft-appft-2
TEST_SUITE += mg-interp-umaddl exit dec-to-lea-32 y-solve

TEST_SUITE_O1 := call-leaf factorial long-int-slot fp-args fp-spill-weight int-loop
TEST_SUITE_O1 += many-add-mul read-write-global-array
TEST_SUITE_O1 += csr-example lsr-simple global-const global-fp-mul fp-loop-simple fp-loop
TEST_SUITE_O1 += char-arg c-print-results-1 c-print-results-call is-1 is-2 is-3 is-4 is-5
TEST_SUITE_O1 += cg-main-1 cg-main-2 cg-main-3 cg-main-4 cg-main-5
TEST_SUITE_O1 += dec-to-lea-32

.PHONY: clean

all:
	for W in $(TEST_SUITE); do \
		make -C $$W PROJECT_DIR=../../..; \
	done

test:
	for W in $(TEST_SUITE); do \
		(make -C $$W stackmaps-check PROJECT_DIR=../../..) || exit 1; \
	done

test-O1:
	for W in $(TEST_SUITE_O1); do \
		(make -C $$W stackmaps-check PROJECT_DIR=../../.. OPT_LEVEL=-O1) || exit 1; \
	done

clean:
	for W in $(TEST_SUITE); do \
		make -C $$W clean; \
	done

