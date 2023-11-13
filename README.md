# Unifico - Unified Address Space and Stack Layout

## Development

### Git Hooks

Git pre-commit hooks in this project are managed by [`pre-commit`][1].
Once you clone the repo locally, run `pre-commit install` to install the configured pre-commit hooks.

[1]: https://pre-commit.com/#usage


### How to compile musl properly.

| LLVM Branch | musl Branch | Description |
|-------------|-------------|-------------|
| llvm-9.0.1  | unmodified  | unmodified  |
| musl        | unasl       | modified    |



### LLVM CMake flags for Unifico

```
-DLLVM_UNIFICO_TABLEGEN_FEATURES="-DUNIFICO_GPR_CALLING_CONV; \
-DUNIFICO_FPR_CALLING_CONV; \
-DUNIFICO_REMAT_RULES; \
-DUNIFICO_REGALLOC_RULES; \
-DUNIFICO_REG_COST; \
-DUNIFICO_INSTR_EXTENSION; \
-DUNIFICO_CHEAP_MOVES; \
-DUNIFICO_AARCH64_TWOADDR;"
```

* Use `llvm-config --unifico-flags` to check which of these are enabled in the current build.


### How to build `init` and `aligned` binaries

* Assumes you use a local config file like `common/nettuno.defs.mk`.
* For init use the `UNMODIFIED=1` flag during `make` invocation.
* This picks the right llvm and musl builds.
* Otherwise, just leave the `UNMODIFIED` undefined.


## Python tools

* `stack-ascii`: Print an ascii representation of an arm/x86 assembly file.
* To install run:

```bash
pin install -e .
```

