olden_benchmarks := olden/treeadd olden/perimeter
prim_benchmarks := prim/bfs

.PHONY: all $(olden_benchmarks) $(prim_benchmarks)

all: $(olden_benchmarks) $(prim_benchmarks)

$(olden_benchmarks) $(prim_benchmarks):
	$(MAKE) --directory=$@ $(TARGET)

clean:
	for d in $(olden_benchmarks) $(prim_benchmarks); do \
		$(MAKE) --directory=$$d clean; \
	done
