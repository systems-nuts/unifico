
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

using std::cerr;
using std::dec;
using std::endl;
using std::hex;
using std::ofstream;
using std::setw;
using std::string;

KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool", "o",
                            "heap_accesses.csv", "Specify output file name");

KNOB<string> FunctionName(KNOB_MODE_WRITEONCE, "pintool", "f", "main",
                          "Function to examine");

ofstream outFile;

UINT64 counter = 0;

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
    if (RTN_Name(rtn) != FunctionName.Value()) {
        return;
    }

    RTN_Open(rtn);

    // For each instruction of the routine
    for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins)) {

        if (!INS_IsMemoryRead(ins))
            continue;

        if (INS_IsStackRead(ins))
            continue;

        counter++;

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
VOID Fini(INT32 code, VOID *v) {}

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
    // Initialize symbol table code, needed for rtn instrumentation
    PIN_InitSymbols();

    // Initialize pin
    if (PIN_Init(argc, argv)) {
        return Usage();
    }

    outFile.open(KnobOutputFile.Value().c_str());

    outFile << "address,step\n";

    // Register Routine to be called to instrument rtn
    RTN_AddInstrumentFunction(Routine, nullptr);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, nullptr);

    // Start the program, never returns
    PIN_StartProgram();

    return 0;
}
