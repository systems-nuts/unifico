Hello all. I would like your insight on the following:
Suppose I have a patch for llvm-9. And, also, that I would like to use just the aligner from the popcorn compiler toolchain (with the minimum necessary modules from the toolchain).
That is, I want to compile x86-64/aarch64 binaries using my own modified version of LLVM and also use the alignment tool, so that my two binaries have their address space aligned, similarly to what happens in the popcorn toolchain.
What would be a good way to do that?
So far, I've tried the following:
   From discussions with Amir and Antonio, it seems that I will need the -name-string-literals and -static-var-sections middle-end passes, as described here.
   There, it is said that we can pass these flags to the opt tool.
   However, I haven't managed yet to incorporate the use of opt and llc into the building of the multi-ISA binaries.
   My approach was to convert this:
HET_CFLAGS := $(CFLAGS) -popcorn-migratable -fno-common \
              -ftls-model=initial-exec
...
%_aarch64.o: %.c
	@echo " [CC] $<"
	@$(CC) $(HET_CFLAGS) -c $(ARM64_INC) -o $(<:.c=.o) $<
   into this:
HET_CFLAGS := $(CFLAGS) -fno-common \
              -ftls-model=initial-exec
HET_OPT_FLAGS := -name-string-literals -static-var-sections -live-values -insert-stackmaps # I keep every pass here, for now. Later, I will keep only the first two.
...
%_aarch64.o: %.c
	@echo " [CC] $<"
	@$(CC) -v $(HET_CFLAGS) -S -emit-llvm $(ARM64_INC) -o $(<:.c=.ll) $<
	@$(OPT) $(HET_OPT_FLAGS) -S $(<:.c=.ll) -o $(<:.c=_opt.ll)
	@$(LLC) -filetype=obj $(<:.c=_opt.ll) -o $@
   i.e. I just removed the popcorn-migratable flag from clang, kept the passes as flags to the opt tool, and added opt and llc as intermediate steps.
   But, I observe that when we add the popcorn-migratable flag to clang (1st snippet), it generates two object files $(BIN)_{aarch64,x86-64}.o , instead of one  $(BIN).o .
   (I don't understand how this logic is hardwired inside clang, whereas in the Makefile we explicitly ask for $(BIN).o as output in the command of the %_aarch64.o: rule.)
   So, removing the popcorn-migratable flag, breaks the building process.
   In a nutshell, how can I use the opt and the llc tools in the building process? (I believe Amir has struggled with it already, thus I would like the input of the others.)
I also have my own LLVM patch to incorporate.
So far, I am looking to modify a little the install_compiler.py script, because it seems to accept one patch in the form llvm-{version}.patch , and I would like to keep my own separate patch.
Do you have a better idea?
(I may have misunderstood some parts of the process, please correct me).
Ideally, I would like to use only the alignment tool, and not have to rely on the whole toolchain to work.
Any ideas would be helpful and sorry for the long post.