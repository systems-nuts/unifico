# Notes on the manual migration of IS

## Compilation

The IS benchmark was built with input class S (small) by issuing:

```
BENCHMARKS=is make CFLAGS="-DUNASL_MIGRATION"
```

## System and Environment

Both executables are renamed to use the same name which in this case is `is_aligned_s.out`.
Moreover, execution uses `/tmp/migration/` as the common working directory and binaries are placed in a subdirectory
named `bin2`.

Execution occurs using a clean environment with `sudo env -i bash` and then executing the corresponding
`env_[hostname].sh` script that makes the corresponding environments match (e.g., by undefining environment variables
present in only one system, umask value, etc.)

Lastly, both systems have Address Space Layout Randomization disabled.

## Manual editing of memory pages

The main difference with the instructions to manually edit criu images that have already been given, relate to the
editing of memory pages (i.e., the `pages-1.img` file).

In the `.data` section which corresponds to page1 (i.e., `vma_0001` is the 2nd page since we are using zero-based 
numbering), there is a reference to the `time.h` syscall that seems to get resolved via vDSO.
This causes a crash on x86_64 upon restoration with criu if we borrow the page directly from the AArch64 dump.
This can be reproduced by using the files in `pages-try1` to recreate this condition.

If we manually patch the offending bytes using the contents of the bytes at offset 0x270 (as also indicated by the
`aligned_map.txt` file produced during linking), using the contents from the x86_64 dump, the process restoration
succeeds.
The memory pages corresponding to this edit are in `pages-try2`.

The better solution is to comment out any time-related syscalls, thus ending up with binaries that do not use the vDSO
to accelerate these calls.
 
### Memory page breakdown

#### Page breakdown of x86_64 memory image

0               .text
1               .data
[2-134]         .bss
[135-136]       vdso
[137-139]       vvar
[140-141]       stack


### Page breakdown of AArch64 memory image

0               .text
1               .data
[2-134]         .bss
[135-136]       vvar
[137-138]       stack
139             vdso

### Page breakdown of manually reconstructed x86_64 image

0               .text  -> zero-filled, copy from x86_64 or AArch64
1               .data  -> copy from AArch64 + patch as described above
[2-134]         .bss   -> copy from AArch64
[135-136]       vdso   -> template, copy from x86_64
[137-139]       vvar   -> template, copy from x86_64
[140-141]       stack  -> copy from AArch64
