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

// typedef std::map<llvm::Value *, dependency_t *> dependency_map_t;

class flow_graph {

  private:
    std::map<llvm::Value *, bool> regCover; // indicate whether
                                            // value was covered
                                            // during liveness
                                            // analysis
    typedef struct live_info {
        std::map<llvm::Value *, bool> live_in;
        std::map<llvm::Value *, bool> live_out;
    } live_info; // typedef one row of the liveness table

    std::map<llvm::Value *, live_info> live_tab; // liveness table

    llvm::Value *root; // the root instruction

    typedef std::map<llvm::Value *, bool> tree_list;

    std::map<llvm::Value *, tree_list> BB_livin; // livein mapped
                                                 // to basic block

    llvm::Module::iterator root_fita;

    int reg_pressure; // maximum register pressure

    llvm::Value *mpr; // at which instr there is max reg pressure
                      //  i.e. max variables are live simultaneously

  public:
    flow_graph(llvm::Module::iterator fita,
               llvm::Module::iterator end); // creates the CFG

    int liveness_flow(llvm::Value *op,
                      llvm::ilist_iterator<llvm::Instruction> iita,
                      llvm::BasicBlock *bita);
    // populates liveness info
    int calculate_reg_pressure(); // interference
                                  // graph

    std::map<llvm::Value *, bool> // a map of instructions
    BBLiveness(llvm::BasicBlock *bita, tree_list live_in);

    int // a map of instructions
    all_BB_liveness(llvm::Function *bita);

    bool check_livein(std::map<llvm::Value *, bool>,
                      llvm::BasicBlock *bb); // check if there
                                             // was any change in
                                             // live_in when
                                             // recursing over BBs

    bool empty_the_maps();
    int return_reg_pressure();

    llvm::Value *max_pressure_instr();

}; // flowgraph

flow_graph::flow_graph(llvm::Module::iterator fita, llvm::Module::iterator end)
{

    // rootBB = new node; //root basic block
    auto aita = fita->arg_begin(); // argument iterator
    auto bita = (*fita).begin();   // basic block iterator
    auto iita = (*bita).begin();   // instruction iterator
    root = iita;                   // store the root iita
    root_fita = fita;
    int name_count = 0;

    while (fita != end) {
        all_BB_liveness(fita); // get the
        fita++;
    }

    reg_pressure = calculate_reg_pressure();

} // flow_graph constructor

std::map<llvm::Value *, bool> // a map of instructions
flow_graph::BBLiveness(llvm::BasicBlock *bita, tree_list live_in)
{

    // take input of live variables that are live in at subsequent basic
    // blocks
    // check until where they are live in this basic block and construct
    // intf. graph
    // accordingly

    auto iita = bita->end();
    iita--;

    auto opcode = iita->getOpcode();
    if (opcode == llvm::Instruction::Call) {
        std::cout << "Call instruction found ! " << std::endl;
    }

    tree_list::iterator it = live_in.begin();

    while (it != live_in.end()) {
        auto init = iita;
        liveness_flow(it->first, iita, bita);
        it++;
    }

    while (iita != (*bita).begin()) { // need to add multiple BB
                                      // liveness analysis

        iita--;
        auto opcode = iita->getOpcode();

        if (opcode == llvm::Instruction::Call) {
            continue; // function name is call argument
                      // It is not defined in the current
                      // fn so generates false liveness
                      // for the rest of the BB
                      // need to handle this properly
                      // for more accuracy
        }

        int numOp = iita->getNumOperands();
        while (numOp > 0) {

            llvm::ConstantInt *CI;
            auto xx = (iita->getOperand(numOp - 1));

            if (!(CI = llvm::dyn_cast<llvm::ConstantInt>(xx))) {
                auto init = iita;
                liveness_flow(xx, init, bita);
            }
            numOp--;
        }
    }

    return live_tab[bita->begin()].live_in; // live_in info
                                            // for the BB
}

int flow_graph::all_BB_liveness(llvm::Function *fita)
{

    auto bita = fita->begin();
    tree_list empty_tree;
    while (bita != fita->end()) {
        BB_livin[bita] = BBLiveness(bita, empty_tree);
        bita++;
    } // got initial liveness info

    bita = fita->begin(); // root BB
    bool stop_flag = false;

    while (!stop_flag) { // iterate liveness calculations
        stop_flag = true;
        while (bita != fita->end()) {
            tree_list succ_map;
            auto sit = succ_begin(bita);
            while (sit != succ_end(bita)) {
                //(*sit)->dump(); //dump the BB
                tree_list live_in_succ = BB_livin[*sit];
                tree_list::iterator it = live_in_succ.begin();
                while (it != live_in_succ.end()) {
                    succ_map[it->first] = true;
                    it++;
                }
                sit++;
            }
            tree_list live_in_new = BBLiveness(bita, succ_map);
            stop_flag &= check_livein(live_in_new, bita);
            BB_livin[bita] = live_in_new;
            bita++;
        }
        bita = fita->begin(); // reset the bita
    }
}

bool flow_graph::check_livein(std::map<llvm::Value *, bool> mm,
                              llvm::BasicBlock *bb)
{
    bool forward_check = true;
    std::map<llvm::Value *, bool>::iterator it_0 = mm.begin();
    while (it_0 != mm.end()) {
        if (BB_livin[bb].find(it_0->first) == BB_livin[bb].end())
            forward_check = false;
        break;
        it_0++;
    }

    bool backward_check = true;
    std::map<llvm::Value *, bool>::iterator it_1 = BB_livin[bb].begin();
    while (it_1 != BB_livin[bb].end()) {

        if (mm.find(it_1->first) == mm.end()) {

            backward_check = false;
            break;
        }
        it_1++;
    }
    return forward_check && backward_check;
};

int flow_graph::liveness_flow(llvm::Value *op,
                              llvm::ilist_iterator<llvm::Instruction> iita,
                              llvm::BasicBlock *bita)
{

    if (regCover[op] == true)
        return 0;
    else if (iita == (*bita).begin()) {
        live_tab[iita].live_in[op] = true;   // instr where
                                             // operand first
        live_tab[iita].live_out[op] = false; // used is live in
                                             // but not
        regCover[op] = true;
    }
    else {
        live_tab[iita].live_in[op] = true;   // instr where
                                             // operand first
        live_tab[iita].live_out[op] = false; // used is live in
                                             //  but not
        // live out
        while (iita != (*bita).begin()) {
            // populate the liveness
            // table
            // iita->dump();//debug
            if (iita == op) {
                iita--;
                live_tab[iita].live_in[op] = false;
                live_tab[iita].live_out[op] = true;
                iita = (*bita).begin(); // breaks out
            }
            else {
                iita--;
                live_tab[iita].live_in[op] = true;
                live_tab[iita].live_out[op] = true;
            }
        }
        regCover[op] = true;
    }
} // liveness flow

int flow_graph::calculate_reg_pressure()
{
    int max_reg_pressure = 0; // max reg _pressure
    std::map<llvm::Value *, live_info>::iterator it = live_tab.begin();
    llvm::Value *max_pressure_instr;
    while (it != live_tab.end()) {
        auto liv_in = (it->second).live_in;
        auto liv_out = (it->second).live_out;
        int reg_pressure_in = liv_in.size();
        int reg_pressure_out = liv_out.size();
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

bool flow_graph::empty_the_maps()
{ // not needed if we make new flowgraph for each regalloc iter
    live_tab.empty();
}

int flow_graph::return_reg_pressure() { return reg_pressure; }

llvm::Value *flow_graph::max_pressure_instr() { return mpr; }

#endif
