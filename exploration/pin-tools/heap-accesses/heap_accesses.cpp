
//
// This tool examines how many of the memory accesses make "far" jumps.
// It does this by setting a fixed address every time, and when the program
// accesses memory that lies further for more than a fixed amount, it sets the
// new base address as the last far access.
//

#include "pin.H"
#include <cmath>
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
UINT64 counter = 999;

typedef struct counters {
    UINT64 step = 0;
} COUNTERS;

/*
 * Check the memory location accessed.
 *
 *  addr[in]         Memory location accessed.
 */
static ADDRINT dumpAccess(ADDRINT addr)
{
    counter++;
    //    	if (counter % 1000 != 0)
    //    		return 0;
    outFile << "0x" << std::hex << addr << std::dec << "," << counter << "\n";
    return 0;
}

// Pin calls this function every time a new rtn is executed
VOID Routine(RTN rtn, VOID *v)
{
    if (RTN_Name(rtn) != "spmv_csr") {
        return;
    }

    auto *cnt = (COUNTERS *)v;

    RTN_Open(rtn);

    outFile << "address,step\n";

    // For each instruction of the routine
    for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins)) {

        if (!INS_IsMemoryRead(ins))
            continue;

        if (INS_IsStackRead(ins))
            continue;

        counter++;
        cnt->step++;

        UINT32 memOperands = INS_MemoryOperandCount(ins);
        for (UINT32 memOp = 0; memOp < memOperands; memOp++) {
            if (INS_MemoryOperandIsRead(ins, memOp)) {
                INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)dumpAccess,
                               IARG_MEMORYOP_EA, memOp, IARG_END);
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
    cerr << "This Pintool dumps the memory accesses with an optional step to "
            "skip some of them"
         << endl;
    cerr << endl << KNOB_BASE::StringKnobSummary() << endl;
    return -1;
}

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */

int main(int argc, char *argv[])
{
    UINT32 step = 0;
    if (argc > 1) {
        char **endptr = nullptr;
        step = strtol(argv[1], endptr, 10);
    }

    // Initialize symbol table code, needed for rtn instrumentation
    PIN_InitSymbols();

    outFile.open("heap_accesses.csv");

    // Initialize pin
    if (PIN_Init(argc, argv)) {
        return Usage();
    }

    // Allocate a counter for this routine
    auto *cnt = new COUNTERS;
    cnt->step = step;

    // Register Routine to be called to instrument rtn
    RTN_AddInstrumentFunction(Routine, cnt);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);

    // Start the program, never returns
    PIN_StartProgram();

    return 0;
}
