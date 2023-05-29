
//
// This tool counts the numbers of loads/stores between registers and the
// memory. Arguments:
// - Output file name
// - Function to examine (examines all function if this is empty)
//

#include "pin.H"
#include <fstream>
#include <iomanip>
#include <iostream>

using std::cerr;
using std::dec;
using std::endl;
using std::hex;
using std::ofstream;
using std::setw;
using std::string;

KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool", "o",
                            "heap_accesses.csv", "Specify output file name");

KNOB<string> FunctionName(KNOB_MODE_WRITEONCE, "pintool", "f", "",
                          "Function to examine");

KNOB<bool> ProfileAllMemoryAccesses(
    KNOB_MODE_WRITEONCE, "pintool", "a", "0",
    "Profile all memory accesses, not only mov-like instructions");

ofstream outFile;
static UINT64 load_count = 0;
static UINT64 store_count = 0;

// This function is called before every load to a register is executed
VOID do_load_count() { load_count++; }

// This function is called before every store from a register is executed
VOID do_store_count() { store_count++; }

// Pin calls this function every time a new rtn is executed
VOID Routine(RTN rtn, VOID *v)
{
    if (!FunctionName.Value().empty() &&
        RTN_Name(rtn) != FunctionName.Value()) {
        return;
    }

    RTN_Open(rtn);

    // For each instruction of the routine
    for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins)) {

        // Examine either all memory accesses or only MOV-like instructions
        if (!ProfileAllMemoryAccesses && (INS_Opcode(ins) < XED_ICLASS_MOV ||
                                          INS_Opcode(ins) > XED_ICLASS_MOV_DR))
            continue;

        if (INS_OperandCount(ins) < 2) {
            continue;
        }

        // If not at least one of the operands is a register, continue (e.g., in
        // the case of `movsb`).
        if (!INS_OperandIsReg(ins, 0) && !INS_OperandIsReg(ins, 1))
            continue;

        if (INS_IsMemoryRead(ins)) {
            // Insert a call to load count before every instruction that loads
            // from memory into a register.
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)do_load_count,
                           IARG_END);
        }

        if (INS_IsMemoryWrite(ins)) {
            // Insert a call to store count before every instruction that stores
            // to memory from a register.
            INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)do_store_count,
                           IARG_END);
        }
    }

    RTN_Close(rtn);
}

// This function is called when the application exits.
// It dumps the load/store counters.
VOID Fini(INT32 code, VOID *v)
{
    outFile << load_count << "," << store_count << endl;
    outFile.close();
}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

INT32 Usage()
{
    cerr << "This Pintool calculates the number of loads and stores to memory."
         << endl;
    cerr << endl << KNOB_BASE::StringKnobSummary() << endl;
    return -1;
}

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */

int main(int argc, char *argv[])
{
    // Initialize symbol table code, needed for rtn instrumentation
    PIN_InitSymbols();

    // Initialize pin
    if (PIN_Init(argc, argv)) {
        return Usage();
    }

    outFile.open(KnobOutputFile.Value().c_str());

    outFile << "loads,stores" << endl;

    // Register Routine to be called to instrument rtn
    RTN_AddInstrumentFunction(Routine, nullptr);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, nullptr);

    // Start the program, never returns
    PIN_StartProgram();

    return 0;
}
