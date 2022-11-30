# Unifico - Unified Address Space and Stack Layout

## Development

### Git Hooks

Git pre-commit hooks in this project are managed by [`pre-commit`][1].
Once you clone the repo locally, run `pre-commit install` to install the configured pre-commit hooks.


### How to compile musl properly.

| LLVM Branch | musl Branch | Description |
|-------------|-------------|-------------|
| llvm-9.0.1  | unmodified  | unmodified  |
| musl        | unasl       | modified    |



[1]: https://pre-commit.com/#usage
