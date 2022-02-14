# Installation Prerequisites

## Popcorn compiler toolchain

```bash
git clone git@github.com:ssrg-vt/popcorn-compiler.git
sudo ./install_compiler.py --install-all --threads 8
```

For more info, see https://github.com/ssrg-vt/popcorn-compiler/blob/main/INSTALL .

## LLVM

```bash
git clone https://github.com/blackgeorge-boom/llvm-project
```

## Musl toolchain

```bash
git clone git@github.com:systems-nuts/musl-stack-reloc.git
git checkout unasl

# Fix necessary variables inside install_musl.sh
# LLVM hash should be c6780392ecf34ebf67b011eac483ff6a1fd38dfc from:
# git clone https://github.com/blackgeorge-boom/llvm-project

./install_musl.sh
```

## Stackmaps dump tool

```bash
cd stack-metadata
make clean
make
```

## Run

```bash
cd <top_level>
cd layout/bubblesort
export PYTHONPATH="${PYTHONPATH}:<top_level>"
make clean
make stackmaps-dump
```
