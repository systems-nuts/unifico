
/* Antonio Barbalace, Stevens 2019 */

/* tested only on 64bit architectures */

#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include <elf.h>
#include <limits.h>
#include <link.h>
#include <stdint.h>

#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>

#include "auxv.h"

#define BUFFER_SIZE 128
char buffer[BUFFER_SIZE];

int main(int argc, char *argv[], char *envp[])
{

    printf("argc %d &argc 0x%lx argv 0x%lx\n", argc, (unsigned long)&argc,
           (unsigned long)argv);

    int i;
    for (i = 0; i < argc; i++)
        printf("argv %d at 0x%lx %s\n", i, (unsigned long)argv[i], argv[i]);

    printf("\nenvp 0x%lx\n", (unsigned long)envp);
    i = 0;
    while (envp[i++] != 0)
        printf("envp %d at 0x%lx %s\n", i - 1, (unsigned long)envp[i - 1],
               envp[i - 1]);

    Elf64_Phdr *phdr = 0;
    Elf64_Ehdr *sysinfo_ehdr = 0;
    long phent = 0;
    long phnum = 0;
    Elf64_auxv_t *auxv = (Elf64_auxv_t *)&envp[i];
    printf("\nauxv 0x%lx sizeof(Elf64_auxv_t) %d\n", (unsigned long)auxv,
           (int)sizeof(Elf64_auxv_t));
    for (auxv = (Elf64_auxv_t *)&envp[i]; auxv->a_type != AT_NULL; auxv++)
        switch (auxv->a_type) {
        case AT_SYSINFO_EHDR:
            sysinfo_ehdr = (void *)auxv->a_un.a_val;
            break;
        case AT_PLATFORM:
        case AT_BASE_PLATFORM:
        case AT_EXECFN:
            printf("%s (%d) value %s (0x%lx)\n", at_desc[(int)auxv->a_type],
                   (int)auxv->a_type, (char *)auxv->a_un.a_val,
                   auxv->a_un.a_val);
            break;
        case AT_PHDR:
            phdr = (void *)auxv->a_un.a_val;
            break;
        case AT_PHENT:
            phent = auxv->a_un.a_val;
            break;
        case AT_PHNUM:
            phnum = auxv->a_un.a_val;
            break;
        default:
            printf("%s (%d) value 0x%lx\n", at_desc[(int)auxv->a_type],
                   (int)auxv->a_type, auxv->a_un.a_val);
        };

    printf("\n");
    printf("phdr 0x%lx phent %d (%d) phnum %d\n", (unsigned long)phdr,
           (int)phent, (int)sizeof(Elf64_Phdr), (int)phnum);
    for (i = 0; i < phnum; i++) {
        printf("i: %d type: %d flags: %d off: 0x%lx vaddr: 0x%lx paddr: 0x%lx "
               "filesz: 0x%lx memsz: 0x%lx align: 0x%lx\n",
               i, phdr[i].p_type, phdr[i].p_flags, phdr[i].p_offset,
               phdr[i].p_vaddr, phdr[i].p_paddr, phdr[i].p_filesz,
               phdr[i].p_memsz, phdr[i].p_align);
    }

    if (!sysinfo_ehdr)
        return 0;
    printf("\n");
    printf(
        "sysinfo_ehdr 0x%lx ident %s type %x machine %x version %x entry 0x%lx "
        "poff %lx soff %lx ehsize %x phentsize %x phnum %d shentsize %x shnum "
        "%d shstrndx %d\n",
        (unsigned long)sysinfo_ehdr, sysinfo_ehdr->e_ident,
        sysinfo_ehdr->e_type, sysinfo_ehdr->e_machine, sysinfo_ehdr->e_version,
        sysinfo_ehdr->e_entry, sysinfo_ehdr->e_phoff, sysinfo_ehdr->e_shoff,
        sysinfo_ehdr->e_ehsize, sysinfo_ehdr->e_phentsize,
        sysinfo_ehdr->e_phnum, sysinfo_ehdr->e_shentsize, sysinfo_ehdr->e_shnum,
        sysinfo_ehdr->e_shstrndx);

    Elf64_Phdr *ph = (void *)((char *)sysinfo_ehdr + sysinfo_ehdr->e_phoff);
    size_t *dynv = 0, base = -1;
    for (i = 0; i < sysinfo_ehdr->e_phnum;
         i++, ph = (void *)((char *)ph + sysinfo_ehdr->e_phentsize)) {
        printf("i: %d type: %d flags: %d off: 0x%lx vaddr: 0x%lx paddr: 0x%lx "
               "filesz: 0x%lx memsz: 0x%lx align: 0x%lx\n",
               i, ph->p_type, ph->p_flags, ph->p_offset, ph->p_vaddr,
               ph->p_paddr, ph->p_filesz, ph->p_memsz, ph->p_align);
        if (ph->p_type == PT_LOAD)
            base = (size_t)sysinfo_ehdr + ph->p_offset - ph->p_vaddr;
        else if (ph->p_type == PT_DYNAMIC)
            dynv = (void *)((char *)sysinfo_ehdr + ph->p_offset);
    }
    printf("dynv 0x%lx base 0x%lx\n", (unsigned long)dynv, (unsigned long)base);

    char *strings = 0;
    Elf64_Sym *syms = 0;
    Elf_Symndx *hashtab = 0;
    uint16_t *versym = 0;
    Elf64_Verdef *verdef = 0;

    for (i = 0; dynv[i]; i += 2) {
        void *p = (void *)(base + dynv[i + 1]);
        switch (dynv[i]) {
        case DT_STRTAB:
            strings = p;
            break;
        case DT_SYMTAB:
            syms = p;
            break;
        case DT_HASH:
            hashtab = p;
            break;
        case DT_VERSYM:
            versym = p;
            break;
        case DT_VERDEF:
            verdef = p;
            break;
        }
        printf("dynv %d DT_ %ld @ 0x%lx\n", i, dynv[i], (unsigned long)p);
    }

    printf("\n VDSO dynamic symbols \n"); /* print dynamic symbols */
    for (i = 0; i < hashtab[1]; i++) {
        printf("I %d sym %s section %d value %lx size %ld\n", i,
               strings + syms[i].st_name, syms[i].st_shndx, syms[i].st_value,
               syms[i].st_size);
    }

    printf("\n VDSO sections \n");
    Elf64_Sym *sh_syms = 0;
    Elf_Symndx *sh_hashtab = 0;
    Elf64_Shdr *sh = (void *)((char *)sysinfo_ehdr + sysinfo_ehdr->e_shoff);
    char *sh_strings =
        base + (unsigned long)((Elf64_Shdr *)((char *)sh +
                                              ((sysinfo_ehdr->e_shentsize) *
                                               sysinfo_ehdr->e_shstrndx)))
                   ->sh_offset;

    for (i = 0; i < sysinfo_ehdr->e_shnum;
         i++, sh = (void *)((char *)sh + sysinfo_ehdr->e_shentsize)) {
        // if (sh->sh_type == SHT_STRTAB && sh->sh_addr != 0)
        //	sh_strings = (char*) sh->sh_addr + (unsigned long)base ;
        if (sh->sh_type == SHT_DYNSYM)
            sh_syms = (void *)sh->sh_addr + (unsigned long)base;
        if (sh->sh_type == SHT_HASH)
            sh_hashtab = (void *)sh->sh_addr + (unsigned long)base;

        printf("i: %d name: %d (%s) type: %d flags: 0x%lx addr: 0x%lx offset: "
               "0x%lx size: 0x%lx addralign: 0x%lx entsize: 0x%lx\n",
               i, sh->sh_name, sh_strings ? sh_strings + sh->sh_name : 0,
               sh->sh_type, sh->sh_flags, sh->sh_addr, sh->sh_offset,
               sh->sh_size, sh->sh_addralign, sh->sh_entsize);
    }

    printf(" strings @ 0x%lx, sh_strings @ 0x%lx syms 0x%lx hashtab 0x%lx\n",
           (unsigned long)strings, (unsigned long)sh_strings,
           (unsigned long)sh_syms,
           (unsigned long)sh_hashtab); // they are at the same address --
                                       // duplicated information

    /* Note that the [vvar] section in x86_64 and aarch64 comes right before the
     * [vdso] section, in aarch64 is 1 page up to 5.15 and in x86_64 is 3 pages
     * up to 5.15 -- it has no headers */
    // https://elixir.bootlin.com/linux/latest/source/arch/x86/entry/vdso/vdso-layout.lds.S
    // https://elixir.bootlin.com/linux/latest/source/arch/arm64/kernel/vdso/vdso.lds.S

    // https://elixir.bootlin.com/linux/latest/source/arch/arm64/kernel/vdso.c
    // https://elixir.bootlin.com/linux/latest/source/arch/x86/entry/vdso/vma.c

    /* it seems like they strip the symtab section away in order to have vvar,
     * really strange but we cannot do anything about it! */

    printf("\n");
    int fd = open("/proc/self/maps", O_RDONLY);
    do {
        memset(buffer, 0, BUFFER_SIZE);
        i = read(fd, buffer, BUFFER_SIZE);
        printf("%s", buffer);
    } while (i);

    // sleep(30);

    return 0;
}
