# Various patches to the musl library

## Stack relocation for aarch64

* *antonio.patch*: Antonio Barbalace patch to musl 1.1.21 (see also [here](https://github.com/systems-nuts/musl-stack-reloc))
* *stack-reloc.patch*: A port of Antonio's patch for the musl 1.1.18 inside [popcorn-compiler](https://github.com/ssrg-vt/popcorn-compiler) project
* *stack-reloc-with-x86.patch*: A port of Antonio's patch for relocating both x86-64 and aarch64, on top of the previous patch.
