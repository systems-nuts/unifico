# Useful LLVM flags

| Flag                        | Description                                                                     |   Type | Custom |
|:----------------------------|:--------------------------------------------------------------------------------|-------:|-------:|
| disable-lsr-solver          | Disable loop strength reduction solver                                          |   bool |    Yes |
| simplify-regalloc           | Simplify costs in greedy register allocation                                    |   bool |    Yes |
| aarch64-csr-alignment       | Set the alignment of single callee-saved registers for AArch64 (defaults to 16) |    int |    Yes |
| disable-x86-frame-obj-order | Disable heuristic for frame object ordering in X86 frame lowering               |   bool |    Yes |
| disable-block-align         | Disable alignment at the beginning of basic blocks                              |   bool |    Yes |
| callsite-padding            | JSON file with padding values for callsites                                     | string |    Yes |


# Testing

Run:

```bash
cd <path-to-layout-folder>
make test
```

## Directory structure

* *common/*: Contains some common functionality files

## Installing gdb

* `sudo apt-get install texinfo`
* `sudo apt-get install python-dev`
* [Instructions](http://www.gdbtutorial.com/tutorial/how-install-gdb), but use `./configure --with-python instead`

## Observations - Old

### fact.c 
It seems to be going ok with `-O0`, but with `-O1` the `x29,x30` pair is put on the top of the stack, instead of the bottom.

### call_leaf.c 

####Problem

* X86-64 has more powerful commands that allow operations between memory and regs. 
* Aarch64 does not, so it leads to more loads/stores in memory.

There is some inherent difference between x86 and ARM.
x86 instructions allow arithmetic operations between memory and registers, whereas ARM instructions only allow operations between registers. 

For example, in x86_64 you can do:

```
addl    16(%rbp), %eax
```

To do the same thing with Aarch64 you must first load the mem value into an "intermediate" register and then use it. So, I have an example where this "intermediate" register is first loaded, then stored again (=>difference in stack) and then used for the computation:
```
ldr w8, [x29, #16]
...
str w8, [sp, #4]
...
ldr w16, [sp, #4]
add    w8, w8, w16
```
The reciprocal position in the stack of x86 is not used, so it's not much of a difference, but in general is sounds like a problem:
ARM creates more load instructions to "intermediate" registers -> greater register pressure -> more registers are stored on the stack -> different stack layout.

#### Solution

An optimization flag like `-O1` seems to have fixed this.
`opt` flags: `-mem2reg -sroa`. Also, see `-early-cse -early-cse-mmsa -instcombine -reassociate`
`llc` flags: `-regalloc=basic,fast,greedy, -spiller`

Combinations that almost work:
* mem2reg + fast (maybe search on more opt flags from here) -> Done for O1, go to O2 and more llc

### Note on main()
For the `main` function the frame may not always be fully shown, in the AArch64 case, if x29==sp

## Optimization flags

```
llvm-as < /dev/null | opt -O1 -disable-output -debug-pass=Arguments 2> O1.txt
```
