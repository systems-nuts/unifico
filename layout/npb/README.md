NPB in a flat directory
-----------------------

- Currently support class S, A, and B. Use `make {S | A | B}` or `setclass.sh {S | A | B}`
- Should be built with Popcorn compiler toolchain (http://github.com/ssrg-vt/popcorn-compiler)
- Modified to execute the *core computation* on a remote node.

# How to run

```bash
./run.sh <experiment_name> <class name> [aarch64|x86_64] [unaligned|init]
```
