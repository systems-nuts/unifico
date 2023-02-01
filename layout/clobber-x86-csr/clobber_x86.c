#include <inttypes.h>

uint64_t inc(uint64_t i)
{
    __asm__ __volatile__("" : "+m"(i) : : "r12", "r13", "r14", "r15");
    return i + 1;
}

int main(int argc, char **argv)
{
    (void)argv;
    return inc(argc);
}
