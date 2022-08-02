## Approaches for a unified address space layout

Directories:
* *mappings/*: .tex files describing possible mappings between x86-64 and Aarch64 architectures.
* *spec2017/*: utility scripts and results regarding the execution of the SPEC2017 benchmarks.

### Development

## Git Hooks

Git pre-commit hooks in this project are managed by [`pre-commit`][1].
Once you clone the repo locally, run `pre-commit install` to install the configured pre-commit hooks.


## How to compile musl properly.

| LLVM Branch | musl Branch | Description |
| ---         | ---         | ---         |
| llvm-9.0.1  | unmodified  | unmodified  |
| musl        | unasl       | modified    |



[1]: https://pre-commit.com/#usage
