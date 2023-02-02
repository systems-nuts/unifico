#include <stdio.h>

#include "npbparams.h"

#define TOTAL_KEYS_LOG_2 25
#define NUM_BUCKETS_LOG_2 10

#define MAX_ITERATIONS 10

#define TOTAL_KEYS (1L << TOTAL_KEYS_LOG_2)

int passed_verification;

void c_print_results(char *name, int n1, double t, double mops,
                     char *clinkflags)
{
    printf("--------------------------------------\n");
}

int main(int argc, char **argv)
{
    double timecounter = 0.0;

    if (passed_verification)
        passed_verification = 0;

    c_print_results("IS", 0, timecounter,
                    ((double)(MAX_ITERATIONS * TOTAL_KEYS)) / timecounter,
                    CLINKFLAGS);

    return 0;
}
