#makefile format from 
#http://stackoverflow.com/questions/8440790/how-should-i-link-to-llvm-libraries
CC = g++
LLVM_CONFIG = ~/llvm-13/toolchain/bin/llvm-config

LDFLAGS+=$(shell $(LLVM_CONFIG) --ldflags)
CXXFLAGS+=$(COMMON_FLAGS) $(shell $(LLVM_CONFIG) --cxxflags) -fno-rtti
CPPFLAGS+=$(shell $(LLVM_CONFIG) --cppflags) -I$(shell $(LLVM_CONFIG) --includedir)
LLVMLIBS=$(shell $(LLVM_CONFIG) --libs irreader support)
SYSTEMLIBS=$(shell $(LLVM_CONFIG) --system-libs)

all:
	$(CC) -g main.cpp -std=c++11 $(CXXFLAGS) $(CPPFLAGS) $(LDFLAGS) $(LLVMLIBS) $(SYSTEMLIBS) -o reg_pressure.out

clean:
	rm *.out
