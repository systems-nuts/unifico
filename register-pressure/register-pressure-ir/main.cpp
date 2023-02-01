// this is a test repo that reuses a lot of code from ths aka repo
// found at github.com/tuxfan/ska.git

#include <fstream>
#include <iostream>
#include <list>
#include <stack>
#include <stdlib.h>
#include <string>

#include <llvm/ADT/APInt.h>
#include <llvm/IR/CFG.h>
#include <llvm/IR/Constants.h>
#include <llvm/IR/Function.h>
#include <llvm/IR/InstIterator.h>
#include <llvm/IR/Instruction.h>
#include <llvm/IR/Instructions.h>
#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>
#include <llvm/IRReader/IRReader.h>
#include <llvm/Support/SourceMgr.h>
#include <llvm/Support/raw_ostream.h>

#include "RegAlloc.hh"

llvm::SMDiagnostic llvm_err_;
llvm::LLVMContext llvm_context_;
std::unique_ptr<llvm::Module> llvm_module_;

int main(int argc, char **argv)
{

    if (argc != 2) {
        std ::cout << "Please specify *.ll file as argument " << std::endl;
        exit(0);
    }

    llvm_module_ = llvm::parseIRFile(argv[1], llvm_err_, llvm_context_);

    if (llvm_module_ == nullptr) {
        std::cout << " LLVM parse failed " << std::endl;
        std::cout << llvm_err_.getMessage().str() << std::endl;
    }

    auto fita = llvm_module_->begin(); // the first function
    auto end = llvm_module_->end();

    // need to add code for non-lead functions
    flow_graph *fg = new flow_graph(fita, end); // calculates reg pressure
    // std::cout << " Max register pressure is "
    //	<< fg->return_reg_pressure()
    //	<< " at instruction "
    //	<< std::endl;

    // fg->max_pressure_instr()->dump();

    std::cout << std::endl;

    return 0;
}
