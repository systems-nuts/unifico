
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

KNOB<bool> ProfileStackAccesses(KNOB_MODE_WRITEONCE, "pintool", "s", "0",
                                "Profile stack instead of heap accesses");

KNOB<long int> Granularity(KNOB_MODE_WRITEONCE, "pintool", "g", "0",
                           "Minimum distance between accesses to examine");

ofstream outFile;
UINT64 counter = 0;
ADDRINT init_addr = 0;

/*
 * Check the memory location accessed.
 *
 *  addr[in]         Memory location accessed.
 */
static VOID dumpAccess(ADDRINT addr, ADDRINT *init_addr)
{
    counter++;
    if (Granularity) {
        if (abs((long int)addr - (long int)(*init_addr)) > Granularity) {
            *init_addr = addr;
            outFile << "0x" << std::hex << addr << std::dec << "," << counter
                    << "\n";
        }
        return;
    }
    //    	if (counter % 1000 != 0)
    //    		return 0;
    outFile << "0x" << std::hex << addr << std::dec << "," << counter << "\n";
}

// Pin calls this function every time a new rtn is executed
VOID Routine(RTN rtn, VOID *v)
{
    std::string rtnName = RTN_Name(rtn);
    if (rtnName[0] == '.' || (rtnName[0] == '_' && rtnName[1] != 'Z')) {
        return;
    }
    if (rtnName.find(FunctionName.Value()) == std::string::npos) {
        return;
    }

    RTN_Open(rtn);

    // For each instruction of the routine
    for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins)) {

        if (!INS_IsMemoryRead(ins))
            continue;

        if (INS_IsStackRead(ins) && !ProfileStackAccesses)
            continue;

        if (!INS_IsStackRead(ins) && ProfileStackAccesses)
            continue;

        counter++;

        UINT32 memOperands = INS_MemoryOperandCount(ins);
        for (UINT32 memOp = 0; memOp < memOperands; memOp++) {
            if (INS_MemoryOperandIsRead(ins, memOp)) {
                INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)dumpAccess,
                               IARG_MEMORYOP_EA, memOp, IARG_PTR, &init_addr,
                               IARG_END);
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
