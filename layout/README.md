## Installing gdb

* `sudo apt-get install texinfo`
* `sudo apt-get install python-dev`
* [Instructions](http://www.gdbtutorial.com/tutorial/how-install-gdb), but use `./configure --with-python instead`

## Observations

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

### Note on main()
For the `main` function the frame may not always be fully shown, in the AArch64 case, if x29==sp
