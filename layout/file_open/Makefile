BIN := file_open
SRC := $(BIN).c

modified: init
	mv file_open_aarch64_init.out modified.out
	sshpass -f "/home/nikos/docs/pass.txt" scp modified.out nikos@sole:/home/nikos/phd/unified_abi/layout/file_open

vanilla: init
	mv file_open_aarch64_init.out vanilla.out
	sshpass -f "/home/nikos/docs/pass.txt" scp vanilla.out nikos@sole:/home/nikos/phd/unified_abi/layout/file_open

include ../common/common.mk
