diff --git a/lib/musl-1.1.18/Makefile b/lib/musl-1.1.18/Makefile
index 2f43e6d2..6afccd6e 100644
--- a/lib/musl-1.1.18/Makefile
+++ b/lib/musl-1.1.18/Makefile
@@ -120,10 +120,12 @@ obj/src/internal/version.o obj/src/internal/version.lo: obj/src/internal/version
 
 obj/crt/rcrt1.o obj/ldso/dlstart.lo obj/ldso/dynlink.lo: $(srcdir)/src/internal/dynlink.h $(srcdir)/arch/$(ARCH)/reloc.h
 
-obj/crt/crt1.o obj/crt/scrt1.o obj/crt/rcrt1.o obj/ldso/dlstart.lo: $(srcdir)/arch/$(ARCH)/crt_arch.h
+obj/crt/crt1.o obj/crt/Scrt1.o obj/crt/rcrt1.o obj/ldso/dlstart.lo: $(srcdir)/arch/$(ARCH)/crt_arch.h
 
 obj/crt/rcrt1.o: $(srcdir)/ldso/dlstart.c
 
+obj/crt/Scrt1.o: $(srcdir)/crt/crt1.c
+
 obj/crt/Scrt1.o obj/crt/rcrt1.o: CFLAGS_ALL += -fPIC
 
 obj/crt/$(ARCH)/crti.o: $(srcdir)/crt/$(ARCH)/crti.s
diff --git a/lib/musl-1.1.18/arch/aarch64/crt_arch.h b/lib/musl-1.1.18/arch/aarch64/crt_arch.h
index b64fb3dd..dbc6e8e6 100644
--- a/lib/musl-1.1.18/arch/aarch64/crt_arch.h
+++ b/lib/musl-1.1.18/arch/aarch64/crt_arch.h
@@ -13,3 +13,30 @@ START ":\n"
 "	and sp, x0, #-16\n"
 "	b " START "_c\n"
 );
+
/* TODO copy more than a byte at the time */
#define __memcpy_nostack(dest, src, n)                                         \
    ({                                                                         \
        unsigned long retval = -1;                                             \
        __asm__ volatile(".weak __memcpy_nostack \n"                           \
                         ".weak __memcpy_nostack_exit \n"                      \
                         ".weak __memcpy_nostack_copy \n"                      \
                         "__memcpy_nostack:"                                   \
                         "mov x4, %1 \n\t"                                     \
                         "cmp %2, x4 \n\t"                                     \
                         "b.le __memcpy_nostack_exit \n"                       \
                         "__memcpy_nostack_copy:"                              \
                         "ldrb w5, [%4, x4] \n\t"                              \
                         "strb w5, [%3, x4] \n\t"                              \
                         "add x4, x4, #0x1 \n\t"                               \
                         "cmp %2, x4 \n\t"                                     \
                         "b.gt __memcpy_nostack_copy \n"                       \
                         "__memcpy_nostack_exit:"                              \
                         "mov %0, x4 \n\t"                                     \
                         : "=r"(retval)                                        \
                         : "I"(0), "r"(n), "r"(dest), "r"(src)                 \
                         : "x5", "x4", "memory");                              \
        retval;                                                                \
    })
    + +/* comment the following to disable relocation before libc start */
          +#define STACK_RELOC diff-- git a /
          lib / musl -
    1.1.18 / arch / aarch64 / stack_arch.h b / lib / musl -
    1.1.18 / arch / aarch64 /
        stack_arch.h new file mode 100644 index 00000000..bfb95445 -- - / dev /
        null++ +
    b / lib / musl - 1.1.18 / arch / aarch64 / stack_arch.h @ @-0,
    0 + 1,
    37 @ @+ +/* Original version by the musl authors */
        +    /* Current version by Antonio Barbalace, Stevens 2019 */
        + +#define arch_stack_get() +
        ({
            unsigned long stack_ptr = -1;
            +__asm__ volatile("mov %0, sp\n\t" +
                              : "=r"(stack_ptr) +
                              :
                              : "memory");
            +stack_ptr;
        }) +
        +/* stack relocation configuration parameters */
        + +#define STACK_MB(1024 * 1024) +
#define STACK_SIZE(16 * STACK_MB) +
#define STACK_END_ADDR(0x800000000000) +
#define STACK_START_ADDR(STACK_END_ADDR - STACK_SIZE) +
#define STACK_PAGE_SIZE(4096) +#define STACK_MAPPED_PAGES(32) +
        +/* stack relocation arch dep macros */
        + +#define arch_stack_switch(stack_top, stack_offset) +
        ({
            __asm__ volatile("sub %1, %0, %1 \n\t" + "mov sp, %1 \n\t" +
                             :
                             : "r"(stack_top), "r"(stack_offset) +
                             : "memory");
        }) +
        +   /* TODO maybe move the following */
        + + // applies to linux only
          + +#define arch_vvar_get_pagesz()(STACK_PAGE_SIZE * 1) +
        + // per arch/platform (wasn't able to find this anywhere else in the
          // code)
            + +#define arch_vaddr_max()(0x1000000000000)diff-- git a
            / lib / musl
        - 1.1.18 / crt / crt1.c b / lib / musl -
        1.1.18 / crt / crt1.c index af02af94..9512e85d 100644 -- -a / lib / musl
        - 1.1.18 / crt / crt1.c++ +
        b / lib / musl - 1.1.18 / crt / crt1.c @ @-1,
    18 + 1,
    299 @ @+   /* Original version by the musl authors */
            +  /* Current version by Antonio Barbalace, Stevens 2019 */
            + +/* The current version supports aarch64 stack relocation, but can
              compile
              + * on any architecture. Support for stack relocation on other
              architecture is
              + * future work. A couple of heurisitcs are used in order to keep
              code compact.
              + * It also relocate the [vdso] and [var], it protects the upper
              memory so
              + * malloc cannot use it to allocate anything.
              + */
            +
#include <features.h>

#define START "_start"

#include "crt_arch.h"

            +#ifdef STACK_RELOC
            + #define _GNU_SOURCE + #include "stack_arch.h" +
#include "syscall.h" + #include < sys / prctl.h> + #include < elf.h> +
#include <string.h> + #include<unistd.h> + #include<sys / mman.h> +
            +#if ULONG_MAX
        == 0xffffffff + typedef Elf32_auxv_t Auxv;
+ typedef Elf32_Ehdr Ehdr;
+ #else + typedef Elf64_auxv_t Auxv;
+ typedef Elf64_Ehdr Ehdr;
+ #endif +
#endif /* STACK_RELOC */
    +int main();
void _init() __attribute__((weak));
void _fini() __attribute__((weak));
_Noreturn int __libc_start_main(int (*)(), int, char **, void (*)(), void (*)(),
                                void (*)());
+ + #ifdef STACK_RELOC_DEBUG +
    static inline char *_itoa_b16(char *p, unsigned long x) +
{
    +p += (sizeof(unsigned long) * 2) + 1 + 1;
    +*--p = 0;
    +*--p = '\n';
    +do
    {
        +char c = x % 16;
        +*--p = (c < 10) ? ('0' + c) : ('a' + c - 10);
        +x /= 16;
        +
    }
    while (x)
        ;
    +return p;
    +
}
+ static inline char *_itoa_b10(char *p, long x) +
{
    +char sign = 0;
    +p += 20 + 1 + 1;
    +*--p = 0;
    +*--p = '\n';
    +if (x < 0)
    {
        +x *= -1;
        +sign = 1;
        +
    }
    +do
    {
        +*--p = '0' + x % 10;
        +x /= 10;
        +
    }
    while (x)
        ;
    +if (sign) + *--p = '-';
    +return p;
    +
}
+ #endif /* STACK_RELOC_DEBUG */

    void
    _start_c(long *p)
{
    -int argc = p[0];
    -char **argv = (void *)(p + 1);
    +register int argc = p[0];
    +register char **argv = (void *)(p + 1);
    + +#ifdef STACK_RELOC + /* stack relocation code */
        +register char **envp = argv + argc + 1;
    +Auxv *auxv;
    +int i, copied = -1, size = -1, total_size = -1;
    +long stack_ptr = -1, stack_addr = -1;
    +register long max;
    long vvar_base, vdso_size;
    +Ehdr *sysinfo_ehdr;
    + +/* ARCH getting the the current stack pointer */
      +stack_ptr = arch_stack_get();
    + +/* check if relocation is not needed. This may happen when the current
+	 * stack is below the requested stack address.
+	 */
        +if (STACK_START_ADDR > (unsigned long)stack_ptr) +
        goto _abort_relocation;
    + +/* getting the current dimension of the stack, using heuristics */
      +for (i = 0; i < argc; i++)
    {
        +if (max < (long)argv[i]) + max = (long)argv[i];
        +
    }
    +for (i = 0; envp[i]; i++)
    {
        +if (max < (long)envp[i]) + max = (long)envp[i];
        +
    }
    +auxv = (Auxv *)(&envp[i + 1]);
    +for (i = 0; (auxv[i].a_type != AT_NULL); i++)
    {
        +if (max < (long)auxv[i].a_un.a_val) + max = (long)auxv[i].a_un.a_val;
        + +/* look for VDSO information */
            +if ((auxv[i].a_type ==
                  AT_SYSINFO_EHDR)) /* TODO maybe consider AT_SYSINFO as well */
            + sysinfo_ehdr = (Ehdr *)auxv[i].a_un.a_val;
        + +/* check if we need to abort relocation, for example in case of
   dynamic +	 * linking. The key heuristic is to check if the text section is
   above +	 * the new stack address -- as we don't relocate the text
   section, we +	 * need to abort.
   +	 */
            +if ((auxv[i].a_type == AT_ENTRY) &&
                 +(auxv[i].a_un.a_val >= STACK_END_ADDR)) +
            goto _abort_relocation;
        +
    }
    +/* align max address */
        +max = (max & ~(STACK_PAGE_SIZE - 1)) + STACK_PAGE_SIZE;
    +size = (max - ((unsigned long)stack_ptr));
    + +/* update expected total mapped size in [stack] */
      +total_size =
        STACK_PAGE_SIZE * (STACK_MAPPED_PAGES + (size / STACK_PAGE_SIZE) +
                           1); // it is ok to over estimate this
    + +                        /* if VDSO is mapped in, let's move it firstly */
      +if (sysinfo_ehdr)
    {
        +/* VDSO: need to look up the size in the phdr and align it */
            +Elf64_Phdr *ph =
            (void *)((char *)sysinfo_ehdr + sysinfo_ehdr->e_phoff);
        +size_t base = -1i, end = -1;
        +for (i = 0; i < sysinfo_ehdr->e_phnum;
              i++, ph = (void *)((char *)ph + sysinfo_ehdr->e_phentsize))
        {
            +/* so far, kernel version 5.15 there is only one PT_LOAD, this
                doesn't support more than one */
                +if (ph->p_type == PT_LOAD)
            {
                +base = (size_t)sysinfo_ehdr + ph->p_offset - ph->p_vaddr;
                +end = base + ph->p_memsz;
                +if (end & (STACK_PAGE_SIZE - 1)) + end =
                    (end & ~(STACK_PAGE_SIZE - 1)) + STACK_PAGE_SIZE;
                +
            }
            +
        }
        +if (!base || !end) + goto _malformed_vdso;
        + +/* VVAR: it is before the VDSO, get the size by using a macro */
          +vvar_base = base - arch_vvar_get_pagesz();
        + +/* remap VVAR and VDSO together at the end of the rebuilt address
              space */
          +stack_addr =
            __syscall(SYS_mremap, vvar_base, (base - vvar_base),
                      (base - vvar_base), (MREMAP_FIXED | MREMAP_MAYMOVE),
                      STACK_END_ADDR - (end - vvar_base));
        +if (((unsigned long)stack_addr) > -4096UL)
        {
            +i = 1;
            goto _error;
            +
        }
        + +stack_addr = __syscall(SYS_mremap, base, (end - base), (end - base),
                                  (MREMAP_FIXED | MREMAP_MAYMOVE),
                                  STACK_END_ADDR - (end - base));
        +if (((unsigned long)stack_addr) > -4096UL)
        {
            +i = 2;
            goto _error;
            +
        }
        + +/* update max, size, total size */
          +vdso_size = (end - vvar_base);
        +
    }
    +_malformed_vdso
        : + +#if STACK_RELOC_USE_MMAP + /* get the memory for the stack */
        + + // TODO implement the same trick as with mremap (see below)
          + +#ifdef SYS_mmap2 +
        stack_addr = (void *)__syscall(
        SYS_mmap2, STACK_START_ADDR - vdso_size, STACK_SIZE,
        PROT_READ | PROT_WRITE, (MAP_PRIVATE | MAP_ANON | MAP_FIXED), -1, 0);
    +#else /* SYS_mmap2 */
        + stack_addr = (void *)__syscall(
        SYS_mmap, STACK_START_ADDR - vdso_size, STACK_SIZE,
        PROT_READ | PROT_WRITE, (MAP_PRIVATE | MAP_ANON | MAP_FIXED), -1, 0);
    +#endif /* !SYS_mmap2 */
        + if (((unsigned long)stack_addr) > -4096UL)
    {
        +i = 3;
        goto _error;
        +
    }
    +memset(stack_addr, STACK_SIZE, 0);
    +#endif /* STACK_RELOC_USE_MMAP */
        + + /* rewrite pointers for the new stack */
          +for (i = 0; i < argc; i++) +
        argv[i] =
        (void *)(STACK_END_ADDR - vdso_size - (max - (unsigned long)argv[i]));
    +for (i = 0; envp[i]; i++) + envp[i] =
        (void *)(STACK_END_ADDR - vdso_size - (max - (unsigned long)envp[i]));
    +for (i = 0; (auxv[i].a_type != AT_NULL); i++) + switch (auxv[i].a_type)
    {
        +case AT_PHDR : case AT_BASE : case AT_ENTRY : +case AT_PLATFORM
            : case AT_BASE_PLATFORM : +case AT_EXECFN : case AT_RANDOM
            : +/* check if it is != 0 and greater than the new stack end addr */
              +if (auxv[i].a_un.a_val > STACK_END_ADDR) +
            auxv[i].a_un.a_val =
            STACK_END_ADDR - vdso_size - (max - auxv[i].a_un.a_val);
        + +/* we don't do VDSO relocation for now (TODO fix when we do VDSO
              relocation) */
            +case AT_SYSINFO : case AT_SYSINFO_EHDR
            : +if (vdso_size && auxv[i].a_un.a_val) +
            auxv[i].a_un.a_val =
            STACK_END_ADDR - vdso_size + arch_vvar_get_pagesz();
        +/* all others handled by the kernel */
            +case AT_HWCAP : case AT_PAGESZ : case AT_CLKTCK : case AT_PHENT
            : +case AT_PHNUM : case AT_FLAGS : case AT_UID : case AT_EUID
            : +case AT_GID : case AT_EGID : case AT_SECURE : case AT_EXECFD
            : +case AT_HWCAP2 : +break;
        +
    }
    +/* update pointers with the new address */
        +argv = (void *)(STACK_END_ADDR - vdso_size -
                         ((unsigned long)max - (unsigned long)argv));
    +envp = (void *)(STACK_END_ADDR - vdso_size -
                     ((unsigned long)max - (unsigned long)envp));
    +auxv = (void *)(STACK_END_ADDR - vdso_size -
                     ((unsigned long)max -
                      (unsigned long)auxv)); // i includes the number of auxvs
    + +#if STACK_RELOC_USE_MMAP +
        /* ARCH copy of the stack */ // TODO can we use SYS_mremap instead?
        +copied =
        __memcpy_nostack((STACK_END_ADDR - vdso_size - size), stack_ptr, size);
    +if (copied != size)
    {
        +i = 4;
        goto _error;
        +
    }
    +#else /* STACK_RELOC_USE_MMAP */
        + __retry_mremap
        : +/* try mremap */
          +stack_addr = __syscall(SYS_mremap, (max - total_size), total_size,
                                  total_size, (MREMAP_FIXED | MREMAP_MAYMOVE),
                                  STACK_END_ADDR - vdso_size - total_size);
    +if (((unsigned long)stack_addr) > -4096UL)
    {
        +/*
+		 * Here we use another pseudo heuristic from the Linux kernel.
+		 * When execve the kernel mm_init a stack of one page, then
+		 * in setup_arg_pages it extends it, the extension is 32 pages
+		 * that takes it to 33, however, sometimes is 34 (on aarch64 at
+		 * least). Setting ulimit may also end up in a smaller stack. We
+		 * try to guess the size here.
+		 */
            +if (total_size > size)
        {
            +total_size -= STACK_PAGE_SIZE;
            +goto __retry_mremap;
            +
        }
        +i = 4;
        goto _error;
        +
    }
    +#endif /* !STACK_RELOC_USE_MMAP */
        + + /* tells to the kernel where is the stack */
          +__syscall(SYS_prctl, PR_SET_MM, PR_SET_MM_START_STACK,
                     (STACK_END_ADDR - vdso_size - total_size), 0, 0);
    +__syscall(SYS_prctl, PR_SET_MM, PR_SET_MM_ARG_START, argv[0], 0, 0);
    +__syscall(SYS_prctl, PR_SET_MM, PR_SET_MM_ARG_END, envp[0], 0, 0);
    +__syscall(SYS_prctl, PR_SET_MM, PR_SET_MM_ENV_START, envp[0], 0, 0);
    +__syscall(SYS_prctl, PR_SET_MM, PR_SET_MM_ENV_END,
               STACK_END_ADDR - vdso_size, 0, 0);
    __syscall(SYS_prctl, PR_SET_MM, PR_SET_MM_AUXV, &auxv[0], i * sizeof(Auxv),
              0);
    + +/* mmap protect upper area */
      +__syscall(SYS_mmap, STACK_END_ADDR, arch_vaddr_max() - STACK_END_ADDR, 0,
                 (MAP_PRIVATE | MAP_ANON | MAP_FIXED), -1, 0);
    + +/* ARCH stack switch */
      +arch_stack_switch(STACK_END_ADDR - vdso_size, size);
    + +#if STACK_RELOC_USE_MMAP + /* unmap previous stack */
        +__syscall(SYS_munmap, (max - total_size), total_size);
    +#endif /* STACK_RELOC_USE_MMAP */
        + + /* WARNING here local variables may not work */
          + +_abort_relocation : +#endif /* STACK_RELOC */
        + +                              /* now continue to normal startup */
          +__libc_start_main(main, argc, argv, _init, _fini, 0);
    + +#ifdef STACK_RELOC + /* we should reach here only in case of errors */
        +_error : +
    {
        +char serror[] = "crt1.c: _start_c ERROR 0\n";
        +char verror[22];
        +serror[23] += i;
        +__syscall(SYS_write, 2, serror, strlen(serror));
        + +#ifdef STACK_RELOC_DEBUG +
            memset(verror, '0', sizeof(unsigned long) * 2 + 1);
        +_itoa_b16(verror, (unsigned long)max);
        +__syscall(SYS_write, 2, verror, strlen(verror));
        + +memset(verror, '0', sizeof(unsigned long) * 2 + 1);
        +_itoa_b16(verror, (unsigned long)total_size);
        +__syscall(SYS_write, 2, verror, strlen(verror));
        + +memset(verror, '0', 20);
        +_itoa_b10(verror, (long)stack_addr);
        +__syscall(SYS_write, 2, verror, strlen(verror));
        + +while (1){}; // debugging trap
        +#endif         /* STACK_RELOC_DEBUG */
    }
    +                                  /* from src/exit/_Exit.c */
        +                              // int ec =1;
        +__syscall(SYS_exit_group, 1); // ec);
    +for (;;) __syscall(SYS_exit, 1);  // ec);
    +#endif                            /* STACK_RELOC */
        +
}
+ diff-- git a /
        lib / musl -
    1.1.18 / test - stack - reloc / auxv.h b / lib / musl - 1.1.18 / test -
    stack -
    reloc / auxv.h new file mode 100644 index 00000000..45975ad6 -- - / dev /
        null++ +
    b / lib / musl - 1.1.18 / test - stack - reloc / auxv.h @ @-0,
    0 + 1,
    16 @ @+ +/* Antonio Barbalace, Stevens 2019 */
    + +char *at_desc[] = {"AT_NULL",
                          "AT_IGNORE",
                          "AT_EXECFD",
                          "AT_PHDR",
                          +"AT_PHENT",
                          "AT_PHNUM",
                          "AT_PAGESZ",
                          "AT_BASE",
                          +"AT_FLAGS",
                          "AT_ENTRY",
                          "AT_NOTELF",
                          "AT_UID",
                          +"AT_EUID",
                          "AT_GID",
                          "AT_EGID",
                          "AT_PLATFORM",
                          +"AT_HWCAP",
                          "AT_CLKTCK",
                          "AT_FPUCW",
                          "AT_DCACHEBSIZE",
                          +"AT_ICACHEBSIZE",
                          "AT_UCACHEBSIZE",
                          "AT_IGNOREPPC",
                          "AT_SECURE",
                          +"AT_BASE_PLATFORM",
                          "AT_RANDOM",
                          "AT_HWCAP2",
                          "AT_?",
                          +"AT_?",
                          "AT_?",
                          "AT_?",
                          "AT_EXECFN",
                          +"AT_SYSINFO",
                          "AT_SYSINFO_EHDR",
                          "AT_L1I_CACHESHAPE",
                          "AT_L1D_CACHESHAPE",
                          +"AT_L2_CACHESHAPE",
                          "AT_L3_CACHESHAPE",
                          "AT_?",
                          "AT_?",
                          +"AT_L1I_CACHESIZE",
                          "AT_L1I_CACHEGEOMETRY",
                          "AT_L1D_CACHESIZE",
                          "AT_L1D_CACHEGEOMETRY",
                          +"AT_L2_CACHESIZE",
                          "AT_L2_CACHEGEOMETRY",
                          "AT_L3_CACHESIZE",
                          "AT_L3_CACHEGEOMETRY",
                          +"AT_?",
                          "AT_?",
                          "AT_?",
                          "AT_MINSIGSTKSZ"};
diff-- git a / lib / musl - 1.1.18 / test - stack -
    reloc / compile.sh b / lib / musl - 1.1.18 / test - stack -
    reloc / compile.sh new file mode 100644 index 00000000..7ef843b3 -- - /
        dev / null++ +
    b / lib / musl - 1.1.18 / test - stack - reloc / compile.sh @ @-0,
    0 + 1,
    3 @ @+#! / bin / sh + / usr / local / musl / bin / musl - gcc - o sd self -
        dump.c - static - v + diff-- git a / lib / musl - 1.1.18 / test -
        stack - reloc / self - dump.c b / lib / musl - 1.1.18 / test - stack -
        reloc / self -
        dump.c new file mode 100644 index 00000000..0ef0aded -- - / dev /
            null++ +
        b / lib / musl - 1.1.18 / test - stack - reloc / self - dump.c @ @-0,
    0 + 1,
    172 @ @+ +/* Antonio Barbalace, Stevens 2019 */
        + +   /* tested only on 64bit architectures */
        + +#include<stdio.h> +
#include <link.h> + #include<limits.h> + #include<stdint.h> +
#include <unistd.h> + #include<string.h> + +#include<elf.h> +
        +#include<sys / types.h> + #include<sys / stat.h> + #include<fcntl.h> +
        +#include "auxv.h" + +#define BUFFER_SIZE 128 +
        char buffer[BUFFER_SIZE];
+ + int main(int argc, char *argv[], char *envp[]) +
{
    + +printf("argc %d &argc 0x%lx argv 0x%lx\n", +argc, (unsigned long)&argc,
              (unsigned long)argv);
    + +int i;
    +for (i = 0; i < argc; i++) +
        printf("argv %d at 0x%lx %s\n", +i, (unsigned long)argv[i], argv[i]);
    + +printf("\nenvp 0x%lx\n", (unsigned long)envp);
    +i = 0;
    +while (envp[i++] != 0) + printf("envp %d at 0x%lx %s\n", +i - 1,
                                     (unsigned long)envp[i - 1], envp[i - 1]);
    + +Elf64_Phdr *phdr = 0;
    Elf64_Ehdr *sysinfo_ehdr = 0;
    +long phent = 0;
    long phnum = 0;
    +Elf64_auxv_t *auxv = (Elf64_auxv_t *)&envp[i];
    +printf("\nauxv 0x%lx sizeof(Elf64_auxv_t) %d\n", +(unsigned long)auxv,
            (int)sizeof(Elf64_auxv_t));
    +for (auxv = (Elf64_auxv_t *)&envp[i]; auxv->a_type != AT_NULL; auxv++) +
        switch (auxv->a_type)
    {
        +case AT_SYSINFO_EHDR : +sysinfo_ehdr = (void *)auxv->a_un.a_val;
        +break;
        +case AT_PLATFORM : +case AT_BASE_PLATFORM : +case AT_EXECFN
            : +printf("%s (%d) value %s (0x%lx)\n", +at_desc[(int)auxv->a_type],
                      (int)auxv->a_type, (char *)auxv->a_un.a_val,
                      auxv->a_un.a_val);
        +break;
        +case AT_PHDR : +phdr = (void *)auxv->a_un.a_val;
        +break;
        +case AT_PHENT : +phent = auxv->a_un.a_val;
        +break;
        +case AT_PHNUM : +phnum = auxv->a_un.a_val;
        +break;
        +default : +printf("%s (%d) value 0x%lx\n", +at_desc[(int)auxv->a_type],
                           (int)auxv->a_type, auxv->a_un.a_val);
        +
    };
    + +printf("\n");
    +printf("phdr 0x%lx phent %d (%d) phnum %d\n", +(unsigned long)phdr,
            (int)phent, (int)sizeof(Elf64_Phdr), (int)phnum);
    +for (i = 0; i < phnum; i++)
    {
        +printf("i: %d type: %d flags: %d off: 0x%lx vaddr: 0x%lx paddr: 0x%lx "
                "filesz: 0x%lx memsz: 0x%lx align: 0x%lx\n",
                +i, phdr[i].p_type, phdr[i].p_flags, phdr[i].p_offset,
                phdr[i].p_vaddr, phdr[i].p_paddr, +phdr[i].p_filesz,
                phdr[i].p_memsz, phdr[i].p_align);
        +
    }
    + +if (!sysinfo_ehdr) + return 0;
    +printf("\n");
    +printf("sysinfo_ehdr 0x%lx ident %s type %x machine %x version %x entry "
            "0x%lx " +
                "poff %lx soff %lx ehsize %x phentsize %x phnum %d shentsize "
                "%x shnum %d shstrndx %d\n",
            +(unsigned long)sysinfo_ehdr, sysinfo_ehdr->e_ident,
            sysinfo_ehdr->e_type, sysinfo_ehdr->e_machine,
            +sysinfo_ehdr->e_version, sysinfo_ehdr->e_entry,
            +sysinfo_ehdr->e_phoff, sysinfo_ehdr->e_shoff,
            +sysinfo_ehdr->e_ehsize, sysinfo_ehdr->e_phentsize,
            sysinfo_ehdr->e_phnum, sysinfo_ehdr->e_shentsize,
            +sysinfo_ehdr->e_shnum, sysinfo_ehdr->e_shstrndx);
    + +Elf64_Phdr *ph = (void *)((char *)sysinfo_ehdr + sysinfo_ehdr->e_phoff);
    +size_t *dynv = 0, base = -1;
    +for (i = 0; i < sysinfo_ehdr->e_phnum;
          i++, ph = (void *)((char *)ph + sysinfo_ehdr->e_phentsize))
    {
        +printf("i: %d type: %d flags: %d off: 0x%lx vaddr: 0x%lx paddr: 0x%lx "
                "filesz: 0x%lx memsz: 0x%lx align: 0x%lx\n",
                +i, ph->p_type, ph->p_flags, ph->p_offset, ph->p_vaddr,
                ph->p_paddr, +ph->p_filesz, ph->p_memsz, ph->p_align);
        +if (ph->p_type == PT_LOAD) + base =
            (size_t)sysinfo_ehdr + ph->p_offset - ph->p_vaddr;
        +else if (ph->p_type == PT_DYNAMIC) + dynv =
            (void *)((char *)sysinfo_ehdr + ph->p_offset);
        +
    }
    +printf("dynv 0x%lx base 0x%lx\n", (unsigned long)dynv,
            (unsigned long)base);
    + +char *strings = 0;
    +Elf64_Sym *syms = 0;
    +Elf_Symndx *hashtab = 0;
    +uint16_t *versym = 0;
    +Elf64_Verdef *verdef = 0;
    + +for (i = 0; dynv[i]; i += 2)
    {
        +void *p = (void *)(base + dynv[i + 1]);
        +switch (dynv[i])
        {
            +case DT_STRTAB : strings = p;
            break;
            +case DT_SYMTAB : syms = p;
            break;
            +case DT_HASH : hashtab = p;
            break;
            +case DT_VERSYM : versym = p;
            break;
            +case DT_VERDEF : verdef = p;
            break;
            +
        }
        +printf("dynv %d DT_ %ld @ 0x%lx\n", i, dynv[i], (unsigned long)p);
        +
    }
    + + +printf("\n VDSO dynamic symbols \n"); /* print dynamic symbols */
    +for (i = 0; i < hashtab[1]; i++)
    {
        +printf("I %d sym %s section %d value %lx size %ld\n", +i,
                strings + syms[i].st_name, syms[i].st_shndx, syms[i].st_value,
                syms[i].st_size);
        +
    }
    + +printf("\n VDSO sections \n");
    +Elf64_Sym *sh_syms = 0;
    +Elf_Symndx *sh_hashtab = 0;
    +Elf64_Shdr *sh = (void *)((char *)sysinfo_ehdr + sysinfo_ehdr->e_shoff);
    +char *sh_strings =
        base + (unsigned long)((Elf64_Shdr *)((char *)sh +
                                              ((sysinfo_ehdr->e_shentsize) *
                                               sysinfo_ehdr->e_shstrndx)))
                   ->sh_offset;
    + +for (i = 0; i < sysinfo_ehdr->e_shnum;
            i++, sh = (void *)((char *)sh + sysinfo_ehdr->e_shentsize))
    {
        +     // if (sh->sh_type == SHT_STRTAB && sh->sh_addr != 0)
            + //	sh_strings = (char*) sh->sh_addr + (unsigned long)base ;
            +if (sh->sh_type == SHT_DYNSYM) +
            sh_syms = (void *)sh->sh_addr + (unsigned long)base;
        +if (sh->sh_type == SHT_HASH) + sh_hashtab =
            (void *)sh->sh_addr + (unsigned long)base;
        + +printf("i: %d name: %d (%s) type: %d flags: 0x%lx addr: 0x%lx "
                  "offset: 0x%lx size: 0x%lx addralign: 0x%lx entsize: 0x%lx\n",
                  +i, sh->sh_name, sh_strings ? sh_strings + sh->sh_name : 0,
                  sh->sh_type, sh->sh_flags, sh->sh_addr, sh->sh_offset,
                  +sh->sh_size, sh->sh_addralign, sh->sh_entsize);
        +
    }
    + +printf(" strings @ 0x%lx, sh_strings @ 0x%lx syms 0x%lx hashtab 0x%lx\n",
              (unsigned long)strings, (unsigned long)sh_strings,
              (unsigned long)sh_syms,
              (unsigned long)sh_hashtab); // they are at the same address --
                                          // duplicated information
    + + + + /* Note that the [vvar] section in x86_64 and aarch64 comes right
               before the [vdso] section, in aarch64 is 1 page up to 5.15 and in
               x86_64 is 3 pages up to 5.15 -- it has no headers */
          + // https://elixir.bootlin.com/linux/latest/source/arch/x86/entry/vdso/vdso-layout.lds.S
          + // https://elixir.bootlin.com/linux/latest/source/arch/arm64/kernel/vdso/vdso.lds.S
          + + // https://elixir.bootlin.com/linux/latest/source/arch/arm64/kernel/vdso.c
            + // https://elixir.bootlin.com/linux/latest/source/arch/x86/entry/vdso/vma.c
            + +/* it seems like they strip the symtab section away in order to
                  have vvar, really strange but we cannot do anything about it!
                */
              + +printf("\n");
    +int fd = open("/proc/self/maps", O_RDONLY);
    +do
    {
        +memset(buffer, 0, BUFFER_SIZE);
        +i = read(fd, buffer, BUFFER_SIZE);
        +printf("%s", buffer);
    }
    +while (i);
    + +sleep(30);
    + +return 0;
    +
}
