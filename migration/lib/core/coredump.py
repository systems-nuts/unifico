# Functions and classes for creating core dump from criu images.
# Code is inspired by outdated google coredumper(RIP) [1] and
# fs/binfmt_elf.h from Linux kernel [2].
#
# [1] https://code.google.com/p/google-coredumper/
#     probably already dead, so consider trying:
#     https://github.com/efiop/google-coredumper/
# [2] https://www.kernel.org/
#
# On my x86_64 systems with fresh kernel ~3.17 core dump looks like:
#
#    1) Elf file header;
#    2) PT_NOTE program header describing notes section;
#    3) PT_LOAD program headers for (almost?) each vma;
#    4) NT_PRPSINFO note with elf_prpsinfo inside;
#    5) An array of notes for each thread of the process:
#        NT_PRSTATUS note with elf_prstatus inside;
#        NT_FPREGSET note with elf_fpregset inside;
#        NT_X86_XSTATE note with x86 extended state using xsave;
#        NT_SIGINFO note with siginfo_t inside;
#    6) NT_AUXV note with auxv;
#    7) NT_FILE note with mapped files;
#    8) VMAs themselves;
#
# Or, you can represent it in less details as:
#    1) Elf file header;
#    2) Program table;
#    3) Notes;
#    4) VMAs contents;
#
import io
import sys
import ctypes
import lief

# from . import elf
import elf

# print("from lief: {}".format(self.input_core.notes[0].details[lief.ELF.CorePrStatus.REGISTERS.AARCH64_PC]))

# Some memory-related constants
PAGESIZE = 4096

status = {
    "VMA_AREA_NONE": 0 << 0,
    "VMA_AREA_REGULAR": 1 << 0,
    "VMA_AREA_STACK": 1 << 1,
    "VMA_AREA_VSYSCALL": 1 << 2,
    "VMA_AREA_VDSO": 1 << 3,
    "VMA_FORCE_READ": 1 << 4,
    "VMA_AREA_HEAP": 1 << 5,
    "VMA_FILE_PRIVATE": 1 << 6,
    "VMA_FILE_SHARED": 1 << 7,
    "VMA_ANON_SHARED": 1 << 8,
    "VMA_ANON_PRIVATE": 1 << 9,
    "VMA_AREA_SYSVIPC": 1 << 10,
    "VMA_AREA_SOCKET": 1 << 11,
    "VMA_AREA_VVAR": 1 << 12,
    "VMA_AREA_AIORING": 1 << 13,
    "VMA_AREA_UNSUPP": 1 << 31,
}

prot = {"PROT_READ": 0x1, "PROT_WRITE": 0x2, "PROT_EXEC": 0x4}


def is_seg_of(seg, elf, name=None):
    if len(seg.sections) == 1:
        if name:
            ns = [elf.get_section(name)]
        else:
            ns = [s for s in elf.sections]

        for s in ns:
            if seg.sections[0].virtual_address == s.virtual_address:
                return True

    return False


class elf_note:
    nhdr = None  # Elf_Nhdr;
    owner = None  # i.e. CORE or LINUX;
    data = None  # Ctypes structure with note data;


def align_up(n, alignment):
    r = n % alignment
    return n if r == 0 else n + (alignment - r)


def elf_note_get_ntfile_type(buf):
    hdr_t = elf.elf_x86_64_nt_detail_types.get(elf.NT_FILE)
    hdr = hdr_t.from_buffer_copy(buf)

    names_sz = (
        len(buf)
        - ctypes.sizeof(elf.Elf64_ntfile_hdr_t)
        - ctypes.sizeof(elf.Elf64_ntfile_vma_t) * hdr.count
    )

    fields = elf.Elf64_ntfile_hdr_t._fields_
    fields.append(("vmas", elf.Elf64_ntfile_vma_t * hdr.count))
    fields.append(("rest", ctypes.c_byte * names_sz))

    class elf_files_t(ctypes.Structure):
        _pack_ = 1
        _fields_ = fields

    # files = elf_files_t.from_buffer_copy(buf)
    # files.fnames = []

    # what = bytes(files.rest).decode("utf-8").split("\x00")

    # for i in range(0, hdr.count):
    # files.fnames.append(what[i])

    return elf_files_t


# TODO either preparse or provide an generator interface
def elf_note_get_detail(core, note_type):
    notes = [s for s in core.sections if s.type == lief.ELF.SECTION_TYPES.NOTE]
    mt = core.header.machine_type

    for n in notes:
        buf = n.content
        offset = 0
        nhdr_sz = ctypes.sizeof(elf.Elf64_Nhdr)

        while offset < len(buf):
            nhdr = elf.Elf64_Nhdr.from_buffer_copy(buf[offset:])

            note = elf_note()

            note.nhdr = nhdr
            offset += nhdr_sz

            namesz = align_up(nhdr.n_namesz, 4)
            note.owner = ctypes.create_string_buffer(
                bytes(buf[offset : offset + namesz])
            ).value

            offset += namesz

            descsz = align_up(nhdr.n_descsz, 4)

            if nhdr.n_type == note_type:
                if mt == lief.ELF.ARCH.AARCH64:
                    data_t = elf.elf_aarch64_nt_detail_types.get(note_type)
                else:
                    data_t = elf.elf_x86_64_nt_detail_types.get(note_type)

                if nhdr.n_type == elf.NT_AUXV:
                    num_auxv = int(descsz / ctypes.sizeof(data_t))

                    class elf_auxv(ctypes.Structure):
                        _fields_ = [("auxv", elf.Elf64_auxv_t * num_auxv)]

                    data_t = elf_auxv
                elif nhdr.n_type == elf.NT_FILE:
                    data_t = elf_note_get_ntfile_type(
                        buf[offset : offset + descsz]
                    )

                note.data = data_t.from_buffer_copy(
                    buf[offset : offset + descsz]
                )

                return note

            offset += descsz

    return None


class coredump:
    """
    A class to keep elf core dump components inside and
    functions to properly write them to file.
    """

    ehdr = None  # Elf ehdr;
    phdrs = []  # Array of Phdrs;
    notes = []  # Array of elf_notes;
    vmas = []  # Array of BytesIO with memory content;

    # FIXME keeping all vmas in memory is a bad idea;

    def write(self, f):
        """
        Write core dump to file f.
        """
        buf = io.BytesIO()
        buf.write(self.ehdr)

        for phdr in self.phdrs:
            buf.write(phdr)

        for note in self.notes:
            buf.write(note.nhdr)
            buf.write(note.owner)
            buf.write(b"\0" * (8 - len(note.owner)))
            buf.write(note.data)

        offset = ctypes.sizeof(elf.Elf64_Ehdr())
        offset += (len(self.vmas) + 1) * ctypes.sizeof(elf.Elf64_Phdr())

        filesz = 0
        for note in self.notes:
            filesz += ctypes.sizeof(note.nhdr) + ctypes.sizeof(note.data) + 8

        note_align = PAGESIZE - ((offset + filesz) % PAGESIZE)

        if note_align == PAGESIZE:
            note_align = 0

        if note_align != 0:
            scratch = (ctypes.c_char * note_align)()
            ctypes.memset(ctypes.addressof(scratch), 0, ctypes.sizeof(scratch))
            buf.write(scratch)

        for vma in self.vmas:
            buf.write(vma.data)

        buf.seek(0)
        f.write(buf.read())


class coredump_generator:
    """ Generate core dump.  """

    input_core = None
    output_core = None

    input_executable = None
    output_executable = None

    cores = {}  # cores by pid;
    mms = {}  # mm by pid;
    reg_files = None  # reg-files;
    pagemaps = {}  # pagemap by pid;

    def read(self, file):
        pass

    def __call__(self):
        self.output_core = self._gen_coredump()

        return self.output_core

    def write(self, coredumps_dir):
        with open(coredumps_dir + "/" + "dump-xformed.core", "wb+") as f:
            self.output_core.write(f)

    def _gen_coredump(self):
        """ Generate core dump.  """
        cd = coredump()
        pid = 0  # TODO remove

        # generate everything backwards so it is easier to calculate offset.
        cd.vmas = self._gen_vmas()
        cd.notes = self._gen_notes()
        cd.phdrs = self._gen_phdrs(pid, cd.notes, cd.vmas)
        cd.ehdr = self._gen_ehdr(cd.phdrs)

        return cd

    def _gen_ehdr(self, phdrs):
        """ Generate elf header with program headers phdrs. """
        ehdr = elf.Elf64_Ehdr()

        ctypes.memset(ctypes.addressof(ehdr), 0, ctypes.sizeof(ehdr))
        ehdr.e_ident[elf.EI_MAG0] = elf.ELFMAG0
        ehdr.e_ident[elf.EI_MAG1] = elf.ELFMAG1
        ehdr.e_ident[elf.EI_MAG2] = elf.ELFMAG2
        ehdr.e_ident[elf.EI_MAG3] = elf.ELFMAG3
        ehdr.e_ident[elf.EI_CLASS] = elf.ELFCLASS64
        ehdr.e_ident[elf.EI_DATA] = elf.ELFDATA2LSB
        ehdr.e_ident[elf.EI_VERSION] = elf.EV_CURRENT

        ehdr.e_type = elf.ET_CORE
        ehdr.e_machine = (
            elf.EM_X86_64
            if self.input_core.header.machine_type == lief.ELF.ARCH.AARCH64
            else elf.EM_AARCH64
        )
        ehdr.e_version = elf.EV_CURRENT
        ehdr.e_phoff = ctypes.sizeof(elf.Elf64_Ehdr())
        ehdr.e_ehsize = ctypes.sizeof(elf.Elf64_Ehdr())
        ehdr.e_phentsize = ctypes.sizeof(elf.Elf64_Phdr())
        # FIXME Case len(phdrs) > PN_XNUM should be handled properly.
        # See fs/binfmt_elf.c from linux kernel.
        ehdr.e_phnum = len(phdrs)

        return ehdr

    def _gen_phdrs(self, pid, notes, vmas):
        """ Generate program headers for core dump. """
        phdrs = []

        offset = ctypes.sizeof(elf.Elf64_Ehdr())
        offset += (len(vmas) + 1) * ctypes.sizeof(elf.Elf64_Phdr())

        filesz = 0
        for note in notes:
            filesz += ctypes.sizeof(note.nhdr) + ctypes.sizeof(note.data) + 8

        # PT_NOTE
        phdr = elf.Elf64_Phdr()
        ctypes.memset(ctypes.addressof(phdr), 0, ctypes.sizeof(phdr))
        phdr.p_type = elf.PT_NOTE
        phdr.p_offset = offset
        phdr.p_filesz = filesz

        phdrs.append(phdr)

        note_align = PAGESIZE - ((offset + filesz) % PAGESIZE)

        if note_align == PAGESIZE:
            note_align = 0

        offset += note_align

        # VMA phdrs

        for vma in vmas:
            offset += filesz
            filesz = vma.filesz
            phdr = elf.Elf64_Phdr()
            ctypes.memset(ctypes.addressof(phdr), 0, ctypes.sizeof(phdr))
            phdr.p_type = elf.PT_LOAD
            phdr.p_align = PAGESIZE
            phdr.p_paddr = 0
            phdr.p_offset = offset
            phdr.p_vaddr = vma.start
            phdr.p_memsz = vma.memsz
            phdr.p_filesz = vma.filesz
            phdr.p_flags = vma.flags

            phdrs.append(phdr)

        return phdrs

    def _gen_prpsinfo(self, pid):
        """
        Generate NT_PRPSINFO note for process pid.
        """
        # core = self.cores[pid]

        prpsinfo = elf.elf_prpsinfo()
        ctypes.memset(ctypes.addressof(prpsinfo), 0, ctypes.sizeof(prpsinfo))

        # FIXME TASK_ALIVE means that it is either running or sleeping, need to
        # teach criu to distinguish them.
        TASK_ALIVE = 0x1
        # XXX A bit of confusion here, as in ps "dead" and "zombie"
        # state are two separate states, and we use TASK_DEAD for zombies.
        TASK_DEAD = 0x2
        TASK_STOPPED = 0x3

        # if core["tc"]["task_state"] == TASK_ALIVE:
        # prpsinfo.pr_state = 0
        # if core["tc"]["task_state"] == TASK_DEAD:
        # prpsinfo.pr_state = 4
        # if core["tc"]["task_state"] == TASK_STOPPED:
        # prpsinfo.pr_state = 3

        prpsinfo.pr_state = 0

        # Don't even ask me why it is so, just borrowed from linux
        # source and made pr_state match.
        prpsinfo.pr_sname = (
            b"." if prpsinfo.pr_state > 5 else b"RSDTZW"[prpsinfo.pr_state]
        )
        prpsinfo.pr_zomb = 1 if prpsinfo.pr_state == 4 else 0
        # prpsinfo.pr_nice = core["thread_core"][
        # "sched_prio"] if "sched_prio" in core["thread_core"] else 0
        prpsinfo.pr_nice = 0
        # prpsinfo.pr_flag = core["tc"]["flags"]
        prpsinfo.pr_flag = 0
        # prpsinfo.pr_uid = core["thread_core"]["creds"]["uid"]
        prpsinfo.pr_uid = 0
        # prpsinfo.pr_gid = core["thread_core"]["creds"]["gid"]
        prpsinfo.pr_gid = 0
        prpsinfo.pr_pid = pid
        prpsinfo.pr_ppid = 0
        prpsinfo.pr_pgrp = 0
        prpsinfo.pr_sid = 0
        prpsinfo.pr_psargs = self._gen_cmdline(pid)
        if sys.version_info > (3, 0):
            # prpsinfo.pr_fname = core["tc"]["comm"].encode()
            prpsinfo.pr_fname = "foo".encode()
        else:
            prpsinfo.pr_fname = core["tc"]["comm"]

        name = b"CORE"

        nhdr = elf.Elf64_Nhdr()
        nhdr.n_namesz = len(name) + 1
        nhdr.n_descsz = ctypes.sizeof(elf.elf_prpsinfo())
        nhdr.n_type = elf.NT_PRPSINFO

        note = elf_note()
        note.data = prpsinfo
        note.owner = name
        note.nhdr = nhdr

        return note

    def _gen_prstatus(self):
        """ Generate NT_PRSTATUS note from coredump. """
        in_note = elf_note_get_detail(self.input_core, elf.NT_PRSTATUS)
        in_prstatus = in_note.data

        prstatus = elf.elf_x86_64_prstatus()

        ctypes.memset(ctypes.addressof(prstatus), 0, ctypes.sizeof(prstatus))

        # common data members
        prstatus.pr_info = in_prstatus.pr_info
        prstatus.pr_cursig = in_prstatus.pr_cursig
        prstatus.pr_sigpend = in_prstatus.pr_sigpend
        prstatus.pr_sighold = in_prstatus.pr_sighold
        prstatus.pr_pid = in_prstatus.pr_pid
        prstatus.pr_ppid = in_prstatus.pr_ppid
        prstatus.pr_pgrp = in_prstatus.pr_pgrp
        prstatus.pr_sid = in_prstatus.pr_sid
        prstatus.pr_utime = in_prstatus.pr_utime
        prstatus.pr_stime = in_prstatus.pr_stime
        prstatus.pr_cutime = in_prstatus.pr_cutime
        prstatus.pr_cstime = in_prstatus.pr_cstime
        prstatus.pr_fpvalid = in_prstatus.pr_fpvalid

        # arch-specific data members

        # AArch64 registers that have been excluded from use
        # in_prstatus.pr_reg.x9
        # in_prstatus.pr_reg.x10
        # in_prstatus.pr_reg.x11
        # in_prstatus.pr_reg.x12
        # in_prstatus.pr_reg.x13
        # in_prstatus.pr_reg.x14
        # in_prstatus.pr_reg.x15
        # in_prstatus.pr_reg.x21
        # in_prstatus.pr_reg.x22
        # in_prstatus.pr_reg.x23
        # in_prstatus.pr_reg.x24
        # in_prstatus.pr_reg.x25
        # in_prstatus.pr_reg.x26
        # in_prstatus.pr_reg.x27
        # in_prstatus.pr_reg.x28

        # AArch64 registers that have not been mapped
        # in_prstatus.pr_reg.pstate

        # usage: function arguments
        prstatus.pr_reg.rdi = in_prstatus.pr_reg.x0
        prstatus.pr_reg.rsi = in_prstatus.pr_reg.x1
        prstatus.pr_reg.rdx = in_prstatus.pr_reg.x2
        prstatus.pr_reg.rcx = in_prstatus.pr_reg.x3
        prstatus.pr_reg.r8 = in_prstatus.pr_reg.x4
        prstatus.pr_reg.r9 = in_prstatus.pr_reg.x5

        # usage: temp
        prstatus.pr_reg.r10 = in_prstatus.pr_reg.x6
        prstatus.pr_reg.r11 = in_prstatus.pr_reg.x7

        # usage: temp, varargs, 1st return reg, indirect result location
        prstatus.pr_reg.rax = in_prstatus.pr_reg.x8

        # usage: intra-proc call regs, temp
        prstatus.pr_reg.r13 = in_prstatus.pr_reg.x16
        prstatus.pr_reg.r14 = in_prstatus.pr_reg.x17

        # usage: temp, platform reg
        prstatus.pr_reg.r12 = in_prstatus.pr_reg.x18

        # usage: callee saved regs
        prstatus.pr_reg.rbx = in_prstatus.pr_reg.x19

        # usage: callee saved regs, GOT base pointer (optionally)
        prstatus.pr_reg.r15 = in_prstatus.pr_reg.x20

        # usage: frame pointer (FP) (optionally)
        prstatus.pr_reg.rbp = in_prstatus.pr_reg.x29

        # usage: link register (LR) (optionally), no correspondence
        # in_prstatus.pr_reg.x30

        # usage: stack pointer (SP)
        prstatus.pr_reg.rsp = in_prstatus.pr_reg.sp

        # usage: program counter (PC)
        prstatus.pr_reg.rip = in_prstatus.pr_reg.pc

        # usage: return regs (mapping already done above)
        # prstatus.pr_reg.rax = in_prstatus.pr_reg.x8
        # prstatus.pr_reg.rdx = in_prstatus.pr_reg.x2

        # note packaging, first header info and then data
        nhdr = elf.Elf64_Nhdr()
        nhdr.n_namesz = in_note.nhdr.n_namesz
        nhdr.n_descsz = ctypes.sizeof(prstatus)
        nhdr.n_type = elf.NT_PRSTATUS

        note = elf_note()
        note.nhdr = nhdr
        note.owner = in_note.owner
        note.data = prstatus

        return note

    def _gen_fpregset(self):
        """ Generate NT_FPREGSET note for core dump.  """

        fpregset = elf.elf_fpregset_t()
        ctypes.memset(ctypes.addressof(fpregset), 0, ctypes.sizeof(fpregset))

        # fpregset.cwd = regs["cwd"]
        # fpregset.swd = regs["swd"]
        # fpregset.ftw = regs["twd"]
        # fpregset.fop = regs["fop"]
        # fpregset.rip = regs["rip"]
        # fpregset.rdp = regs["rdp"]
        # fpregset.mxcsr = regs["mxcsr"]
        # fpregset.mxcr_mask = regs["mxcsr_mask"]
        # fpregset.st_space = (ctypes.c_uint * len(regs["st_space"]))(
        # *regs["st_space"])
        # fpregset.xmm_space = (ctypes.c_uint * len(regs["xmm_space"]))(
        # *regs["xmm_space"])

        name = b"CORE"

        nhdr = elf.Elf64_Nhdr()
        nhdr.n_namesz = len(name) + 1
        nhdr.n_descsz = ctypes.sizeof(elf.elf_fpregset_t())
        nhdr.n_type = elf.NT_FPREGSET

        note = elf_note()
        note.nhdr = nhdr
        note.owner = name
        note.data = fpregset

        return note

    def _gen_x86_xstate(self):
        """ Generate NT_X86_XSTATE note for core dump.  """
        data = elf.elf_xsave_struct()
        ctypes.memset(ctypes.addressof(data), 0, ctypes.sizeof(data))

        # data.i387.cwd = fpregs["cwd"]
        # data.i387.swd = fpregs["swd"]
        # data.i387.twd = fpregs["twd"]
        # data.i387.fop = fpregs["fop"]
        # data.i387.rip = fpregs["rip"]
        # data.i387.rdp = fpregs["rdp"]
        # data.i387.mxcsr = fpregs["mxcsr"]
        # data.i387.mxcsr_mask = fpregs["mxcsr_mask"]
        # data.i387.st_space = (ctypes.c_uint * len(fpregs["st_space"]))(
        # *fpregs["st_space"])
        # data.i387.xmm_space = (ctypes.c_uint * len(fpregs["xmm_space"]))(
        # *fpregs["xmm_space"])

        # if "xsave" in fpregs:
        # data.xsave_hdr.xstate_bv = fpregs["xsave"]["xstate_bv"]
        # data.ymmh.ymmh_space = (ctypes.c_uint *
        # len(fpregs["xsave"]["ymmh_space"]))(
        # *fpregs["xsave"]["ymmh_space"])

        nhdr = elf.Elf64_Nhdr()
        nhdr.n_namesz = 6
        nhdr.n_descsz = ctypes.sizeof(data)
        nhdr.n_type = elf.NT_X86_XSTATE

        note = elf_note()
        note.nhdr = nhdr
        note.owner = b"LINUX"
        note.data = data

        return note

    def _gen_siginfo(self):
        """ Generate NT_SIGINFO note for core dump.  """
        siginfo = elf.siginfo_t()

        # FIXME zeroify everything for now
        ctypes.memset(ctypes.addressof(siginfo), 0, ctypes.sizeof(siginfo))

        name = b"CORE"

        nhdr = elf.Elf64_Nhdr()
        nhdr.n_namesz = len(name) + 1
        nhdr.n_descsz = ctypes.sizeof(elf.siginfo_t())
        nhdr.n_type = elf.NT_SIGINFO

        note = elf_note()
        note.nhdr = nhdr
        note.owner = name
        note.data = siginfo

        return note

    def _gen_auxv(self):
        """ Generate NT_AUXV note for core dump.  """

        in_note = elf_note_get_detail(self.input_core, elf.NT_AUXV)

        note = elf_note()
        note.nhdr = in_note.nhdr
        note.owner = in_note.owner
        note.data = in_note.data

        return note

    def _gen_files(self):
        """ Generate NT_FILE note for core dump.  """

        in_note = elf_note_get_detail(self.input_core, elf.NT_FILE)

        nhdr = elf.Elf64_Nhdr()

        name = b"CORE"

        nhdr.n_namesz = len(name) + 1
        nhdr.n_descsz = ctypes.sizeof(in_note.data)
        nhdr.n_type = elf.NT_FILE

        note = elf_note()
        note.nhdr = nhdr
        note.owner = name
        note.data = in_note.data

        return note

    def _gen_thread_notes(self):
        notes = []

        notes.append(self._gen_prstatus())
        # notes.append(self._gen_fpregset())
        # notes.append(self._gen_x86_xstate())
        notes.append(self._gen_siginfo())

        return notes

    def _gen_notes(self):
        """ Generate notes for core dump. """
        notes = []

        # TODO TBD if required
        # notes.append(self._gen_prpsinfo(pid))

        # Main thread first
        notes += self._gen_thread_notes()

        # TODO TBD if required
        # notes.append(self._gen_auxv())

        notes.append(self._gen_files())

        return notes

    def _get_page(self, pid, page_no):
        """
        Try to find memory page page_no in pages.img image for process pid.
        """
        pagemap = self.pagemaps[pid]

        # First entry is pagemap_head, we will need it later to open
        # proper pages.img.
        pages_id = pagemap[0]["pages_id"]
        off = 0  # in pages
        for m in pagemap[1:]:
            found = False
            for i in range(m["nr_pages"]):
                if m["vaddr"] + i * PAGESIZE == page_no * PAGESIZE:
                    found = True
                    break
                off += 1

            if not found:
                continue

        return None

    def _gen_cmdline(self, pid):
        """
        Generate full command with arguments.
        """
        # mm = self.mms[pid]

        # vma = {}
        # vma["start"] = mm["mm_arg_start"]
        # vma["end"] = mm["mm_arg_end"]
        # # Dummy flags and status.
        # vma["flags"] = 0
        # vma["status"] = 0
        # size = vma["end"] - vma["start"]

        # chunk = self._gen_mem_chunk(pid, vma, size)
        chunk = b""

        # Replace all '\0's with spaces.
        return chunk.replace(b"\0", b" ")

    def _get_vma_dump_size(self, vma):
        """
        Calculate amount of vma to put into core dump.
        """
        if (
            vma["status"] & status["VMA_AREA_VVAR"]
            or vma["status"] & status["VMA_AREA_VSYSCALL"]
            or vma["status"] & status["VMA_AREA_VDSO"]
        ):
            size = vma["end"] - vma["start"]
        elif vma["prot"] == 0:
            size = 0
        elif (
            vma["prot"] & prot["PROT_READ"] and vma["prot"] & prot["PROT_EXEC"]
        ):
            size = PAGESIZE
        elif (
            vma["status"] & status["VMA_ANON_SHARED"]
            or vma["status"] & status["VMA_FILE_SHARED"]
            or vma["status"] & status["VMA_ANON_PRIVATE"]
            or vma["status"] & status["VMA_FILE_PRIVATE"]
        ):
            size = vma["end"] - vma["start"]
        else:
            size = 0

        return size

    def _get_vma_flags(self, vma):
        """
        Convert vma flags int elf flags.
        """
        flags = 0

        if vma["prot"] & prot["PROT_READ"]:
            flags = flags | elf.PF_R

        if vma["prot"] & prot["PROT_WRITE"]:
            flags = flags | elf.PF_W

        if vma["prot"] & prot["PROT_EXEC"]:
            flags = flags | elf.PF_X

        return flags

    def _gen_vmas(self):
        """ Generate vma contents for core dump. """
        loads = [
            s
            for s in self.input_core.segments
            if s.type == lief.ELF.SEGMENT_TYPES.LOAD
        ]

        for ls in loads:
            if ls.flags & lief.ELF.SEGMENT_FLAGS.X:
                if is_seg_of(ls, self.input_executable, ".text"):
                    print("text " + hex(ls.virtual_address))
                else:
                    print("skipping X segment at " + hex(ls.virtual_address))
            elif ls.flags & lief.ELF.SEGMENT_FLAGS.W:
                if is_seg_of(ls, self.input_executable, ".bss"):
                    print("bss " + hex(ls.virtual_address))
                else:
                    print("heap/stack segment at " + hex(ls.virtual_address))
            else:
                print("skipping segment at " + hex(ls.virtual_address))

        class vma_class:
            data = None
            filesz = None
            memsz = None
            flags = None
            start = None

        vmas = []
        # for vma in mm["vmas"]:
        # v = vma_class()
        # v.filesz = self._get_vma_dump_size(vma)
        # v.data = self._gen_mem_chunk(pid, vma, v.filesz)
        # v.memsz = vma["end"] - vma["start"]
        # v.start = vma["start"]
        # v.flags = self._get_vma_flags(vma)

        # vmas.append(v)

        return vmas
