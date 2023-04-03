#include <inttypes.h>

uint64_t inc(uint64_t i)
{

    register unsigned r15 __asm("x19") = 0x900003;
    __asm__ __volatile__("" : "+m"(i) : "r"(r15) : "x9", "x24");
    return i + 1;
}

int main(int argc, char **argv)
{
    (void)argv;
    return inc(argc);
}
