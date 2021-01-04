## Observations

* fact.c seems to be going ok
* call_leaf.s has a problem: X86 has more powerful commands that allow operations between memory and regs. Whereas, aarch64 does not, so it leads to more loads/stores in memory.
