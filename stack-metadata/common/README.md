--------
Overview
--------

** Needed for `stack-metadata/`. **

The final step in generating multi-ISA binaries is to parse the generated
.llvm_pcn_stackmaps section and add stack transformation metadata sections to
each binary.  This information provides the return address mappings across
binaries and the live value location information at each call site.

The metadata consists of function addresses & sizes, frame unwinding entries,
call sites and live value locations.  The frame unwinding entries describe
where callee-saved registers are stored in a function's stack frame and
consists of an offset from the frame base pointer and the number of the saved
register (DWARF encoding).  Each call site is denoted by an ID (assigned by the
tool), a return address for the function call, the size of the function's
activation at the call site, the number of unwinding entries and offset into
the unwinding entries section, the number of live values at the call site and
an offset into the live value location section where the records needed to find
live values are located, and the architecture-specific live values and an
offset into architecture-specific live value location records section.

Each live value location record encodes the type of the location (e.g.,
register), the size of the live value, whether or not the value is a pointer,
whether or not the value is a stack-allocated value (an "alloca" in LLVM
parlance) and if so, the size of the stack-allocated data.  Additionally, other
flags specify whether the value is a duplicate record and whether the value is
a temporary materialized just for the stackmap.

The tool adds the following sections to each binary:

.stack_transform.unwind: frame unwinding for all functions
                         (partially added at compile-time)
.stack_transform.unwind_arange: address ranges over which functions span
                                (partially added at compile-time)
.stack_transform.id: call site metadata, sorted by call site ID
.stack_transform.addr: call site metadata, sorted by call site return address
.stack_transform.live: live value location entries
.stack_transform.arch_const: architecture-specific live value location entries

The runtime correlates call sites across architectures by the following
procedure:

1. Calculate the return address for a called function from a source stack frame
2. Use the return address to look up the current ISA's call site record, which
   contains the call site ID
3. Use the call site ID to look up the destination ISA's call site record
4. Populate the return address for the called function from destination ISA's
   call site record, and use both records to copy live values between stacks

There are several generated tools:

- gen-stackinfo: parse the .llvm_pcn_stackmaps section and add stack
  transformation sections to the binary.  This is run once per binary.

- dump-llvm-stackmap: print the raw LLVM-generated stackmap from
  .llvm_pcn_stackmaps in a human-readable format

- dump-stackinfo: print the generated stack transformation metadata in a
  human-readable format

- check-stackmaps: check the generated .llvm_pcn_stackmaps sections of
  two or more binaries for inconsistencies that may prevent a correct
  transformation, e.g., different numbers of stackmaps, different
  numbers of live values at corresponding stackmaps, live values of
  different sizes, inconsistent metadata, etc.

