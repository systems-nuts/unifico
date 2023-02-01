#ifndef RegAlloc_hh
#define RegAlloc_hh

#include <cstring>
#include <fstream>
#include <list>
#include <string>
#include <vector>

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

// typedef std::map<Value *, dependency_t *> dependency_map_t;

using namespace llvm;

class flow_graph {

  private:
    std::map<StringRef, bool> regCover; // indicate whether
    // value was covered
    // during liveness
    // analysis
    typedef struct live_info {
        std::map<StringRef, bool> live_in;
        std::map<StringRef, bool> live_out;
    } live_info; // typedef one row of the liveness table

    std::map<Instruction *, live_info> live_tab; // liveness table

    // Value * root; //the root instruction

    typedef std::map<StringRef, bool> tree_list;

    std::map<BasicBlock *, tree_list> BB_livin; // livein mapped
    // to basic block

    // Module::iterator root_fita ;

    int reg_pressure; // maximum register pressure

    Instruction *mpr; // at which instr there is max reg pressure
                      // i.e. max variables are live simultaneously

  public:
    flow_graph(Module::iterator fita, Module::iterator end); // creates the CFG

    // populates liveness info
    int liveness_flow(StringRef op, Instruction *iita, BasicBlock *bita);

    int calculate_reg_pressure(); // interference graph

    std::map<StringRef, bool> BBLiveness(BasicBlock *bita, tree_list live_in);
    // a map of instructions

    int all_BB_liveness(Module::iterator fita); // a map of instructions

    bool check_livein(std::map<StringRef, bool>, BasicBlock *bb);
    // check if there
    // was any change in
    // live_in when
    // recursing over BBs

    void empty_the_maps();
    int return_reg_pressure();

    Instruction *max_pressure_instr();

}; // flowgraph

flow_graph::flow_graph(Module::iterator fita, Module::iterator end)
{
    // auto aita = fita->arg_begin();//argument iterator
    // int name_count = 0;

    BasicBlock *bita = &*fita->begin(); // basic block iterator

    while (fita != end) {

        all_BB_liveness(fita);
        reg_pressure = calculate_reg_pressure();

        std::cout << fita->getName().str() << "," << reg_pressure << std::endl;

        empty_the_maps();

        fita++;
    }

} // flow_graph constructor

int flow_graph::all_BB_liveness(Module::iterator fita)
{
    auto bita = fita->begin();

    tree_list empty_tree;
    while (bita != fita->end()) {
        BB_livin[&*bita] = BBLiveness(&*bita, empty_tree);
        bita++;
    } // got initial liveness info

    bita = fita->begin(); // root BB
    bool stop_flag = false;

    while (!stop_flag) { // iterate liveness calculations

        stop_flag = true;

        while (bita != fita->end()) {

            tree_list succ_map;
            auto sit = succ_begin(&*bita);

            while (sit != succ_end(&*bita)) {

                //(*sit)->dump(); //dump the BB
                tree_list live_in_succ = BB_livin[*sit];
                tree_list::iterator it = live_in_succ.begin();

                while (it != live_in_succ.end()) {
                    succ_map[it->first] = true;
                    it++;
                }

                sit++;
            }

            tree_list live_in_new = BBLiveness(&*bita, succ_map);
            stop_flag &= check_livein(live_in_new, &*bita);
            BB_livin[&*bita] = live_in_new;
            bita++;
        }

        bita = fita->begin(); // reset the bita
    }
}

// a map of instructions
std::map<StringRef, bool> flow_graph::BBLiveness(BasicBlock *bita,
                                                 tree_list live_in)
{
    // take input of live variables that are live in at subsequent basic
    // blocks
    // check until where they are live in this basic block and construct
    // intf. graph
    // accordingly
    BasicBlock::iterator iita = bita->end();
    iita--;

    auto opcode = iita->getOpcode();
    if (opcode == Instruction::Call) {
        std::cout << "Call instruction found ! " << std::endl;
    }

    tree_list::iterator it = live_in.begin();

    while (it != live_in.end()) {
        auto init = iita;
        liveness_flow(it->first, &*iita, bita);
        it++;
    }

    BasicBlock::iterator first_inst = bita->begin();
    while (!iita->isIdenticalTo(
        &*first_inst)) { // need to add multiple BB liveness analysis

        iita--;
        auto opcode = iita->getOpcode();

        if (opcode == Instruction::Call) {
            continue; // function name is call argument
            // It is not defined in the current
            // fn so generates false liveness
            // for the rest of the BB
            // need to handle this properly
            // for more accuracy
        }

        int numOp = iita->getNumOperands();

        while (numOp > 0) {

            ConstantInt *CI;
            Value *xx = iita->getOperand(numOp - 1);

            if (!(CI = dyn_cast<ConstantInt>(xx))) {
                auto init = iita;
                liveness_flow(xx->getName(), &*init, bita);
            }
            numOp--;
        }
    }

    return live_tab[&*first_inst].live_in; // live_in info for the BB
}

bool flow_graph::check_livein(std::map<StringRef, bool> mm, BasicBlock *bb)
{
    bool forward_check = true;
    std::map<StringRef, bool>::iterator it_0 = mm.begin();
    while (it_0 != mm.end()) {

        if (BB_livin[bb].find(it_0->first) == BB_livin[bb].end())
            forward_check = false;
        break;

        it_0++;
    }

    bool backward_check = true;
    std::map<StringRef, bool>::iterator it_1 = BB_livin[bb].begin();
    while (it_1 != BB_livin[bb].end()) {

        if (mm.find(it_1->first) == mm.end()) {
            backward_check = false;
            break;
        }

        it_1++;
    }

    return forward_check && backward_check;
}

int flow_graph::liveness_flow(StringRef op, Instruction *iita, BasicBlock *bita)
{
    Instruction *first_inst = &*(bita->begin());

    if (regCover[op] == true) {
        return 0;
    }
    else if (iita->isIdenticalTo(first_inst)) { // TODO
        live_tab[iita].live_in[op] = true;      // instr where
        // operand first
        live_tab[iita].live_out[op] = false; // used is live in
        // but not
        regCover[op] = true;
    }
    else {
        live_tab[iita].live_in[op] = true; // instr where
        // operand first
        live_tab[iita].live_out[op] = false; // used is live in
        // but not
        // live out
        while (!iita->isIdenticalTo(first_inst)) { // TODO
            // populate the liveness
            // table
            // iita->dump();//debug
            iita = iita->getPrevNonDebugInstruction();
            if ((iita->getName()).equals(op)) {
                live_tab[iita].live_in[op] = false;
                live_tab[iita].live_out[op] = true;
                iita = first_inst; // breaks out
            }
            else {
                live_tab[iita].live_in[op] = true;
                live_tab[iita].live_out[op] = true;
            }
        }
        regCover[op] = true;
    }
    return 0;
} // liveness flow

int flow_graph::calculate_reg_pressure()
{

    int max_reg_pressure = 0; // max reg _pressure

    std::map<Instruction *, live_info>::iterator it = live_tab.begin();

    Instruction *max_pressure_instr;

    while (it != live_tab.end()) {

        // std::cout << "============\n";
        // it->first->dump(); //debug

        auto liv_in = (it->second).live_in;
        auto liv_out = (it->second).live_out;

        int livein_count = 0;
        int liveout_count = 0;

        // std::cout << "Live in: " << std::endl;
        for (auto const &x : liv_in)
            if (x.second) {
                // std::cout << "    " << x.first.str() << "\n";
                livein_count++;
            }

        // std::cout << "Live out: " << std::endl;
        for (auto const &x : liv_out)
            if (x.second) {
                // std::cout << "    " << x.first.str() << "\n";
                liveout_count++;
            }

        int reg_pressure_in = livein_count;
        int reg_pressure_out = liveout_count;

        if (max_reg_pressure < reg_pressure_in) {
            max_reg_pressure = reg_pressure_in;
            max_pressure_instr = it->first;
        }

        if (max_reg_pressure < reg_pressure_out) {
            max_reg_pressure = reg_pressure_out;
            max_pressure_instr = it->first;
        }

        it++;
    }

    mpr = max_pressure_instr;

    return max_reg_pressure;
}

void flow_graph::empty_the_maps()
{ // not needed if we make new flowgraph for each regalloc iter
    regCover.clear();
    live_tab.clear();
    BB_livin.clear();
}

int flow_graph::return_reg_pressure() { return reg_pressure; }

Instruction *flow_graph::max_pressure_instr() { return mpr; }

#endif
