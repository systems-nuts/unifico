olden_benchmarks := olden/treeadd olden/perimeter
prim_benchmarks := prim/bfs prim/bfs-omp
test_dir := tests

.PHONY: all $(olden_benchmarks) $(prim_benchmarks)

all: $(olden_benchmarks) $(prim_benchmarks)

$(olden_benchmarks) $(prim_benchmarks):
	$(MAKE) --directory=$@ $(TARGET)

test:
	make --directory=$(test_dir) clean
	make --directory=$(test_dir) test

clean:
	for d in $(olden_benchmarks) $(prim_benchmarks); do \
		$(MAKE) --directory=$$d clean; \
	done
