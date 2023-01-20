
//
// This tool examines how many of the memory accesses make "far" jumps.
// It does this by setting a fixed address every time, and when the program
// accesses memory that lies further for more than a fixed amount, it sets the
// new base address as the last far access.
//

#include "pin.H"
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string.h>
using std::cerr;
using std::dec;
using std::endl;
using std::hex;
using std::ofstream;
using std::setw;
using std::string;

ofstream outFile;

ADDRINT init_addr = 0;

// This function is called before every instruction is executed
VOID docount(UINT64 *counter) { (*counter)++; }

/*
 * Check if the memory accessed is further from initial memory access by a fixed
 * offset. For now, the fixed offset is hardcoded.
 *
 *  addr[in]         Memory location accessed.
 *  init_addr[in]    Initial address of the memory accessed.
 */
static ADDRINT IsFarAccess(ADDRINT addr, ADDRINT *init_addr)
{
    if ((long int)addr - (long int)(*init_addr) > 0x500) {
        *init_addr = addr;
        outFile << "Migration"
                << "\n";
    }
    return 0;
}

// Pin calls this function every time a new rtn is executed
VOID Routine(RTN rtn, VOID *v)
{
    if (RTN_Name(rtn) != "spmv_csr")
        return;

    RTN_Open(rtn);

    // For each instruction of the routine
    for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins)) {

        if (!INS_IsMemoryRead(ins))
            continue;

        if (INS_IsStackRead(ins))
            continue;

        UINT32 memOperands = INS_MemoryOperandCount(ins);
        for (UINT32 memOp = 0; memOp < memOperands; memOp++) {
            if (INS_MemoryOperandIsRead(ins, memOp)) {
                INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)IsFarAccess,
                               IARG_MEMORYOP_EA, memOp, IARG_PTR, &init_addr,
                               IARG_END);
            }
        }
    }

    RTN_Close(rtn);
}

// This function is called when the application exits
// It prints the name and count for each procedure
VOID Fini(INT32 code, VOID *v) { return; }

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

INT32 Usage()
{
    cerr << "This Pintool counts the number of times we access data in" << endl;
    cerr << "the heap from a far memory location." << endl;
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

    outFile.open("heap_accesses.out");

    // Initialize pin
    if (PIN_Init(argc, argv))
        return Usage();

    // Register Routine to be called to instrument rtn
    RTN_AddInstrumentFunction(Routine, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);

    // Start the program, never returns
    PIN_StartProgram();

    return 0;
}
