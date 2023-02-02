#include <stdio.h>

#include "npbparams.h"

#define TOTAL_KEYS_LOG_2 25
#define MAX_KEY_LOG_2 21
#define NUM_BUCKETS_LOG_2 10

#define MAX_ITERATIONS 10

#define TOTAL_KEYS (1L << TOTAL_KEYS_LOG_2)

int passed_verification;

void c_print_results(char *name, char class, int n1, int n2, int n3, int niter,
                     double t, double mops, char *optype,
                     int passed_verification, char *npbversion,
                     char *compiletime, char *cc, char *clink, char *c_lib,
                     char *c_inc, char *cflags, char *clinkflags)
{
    printf("--------------------------------------\n");
}

int main(int argc, char **argv)
{
    double timecounter = 0.0;
    printf("%lf, %lf\n", timecounter,
           ((double)(MAX_ITERATIONS * TOTAL_KEYS)) / timecounter / 1000000);

    c_print_results(
        "IS", CLASS, (int)(TOTAL_KEYS / 64), 64, 0, MAX_ITERATIONS, timecounter,
        ((double)(MAX_ITERATIONS * TOTAL_KEYS)) / timecounter / 1000000.,
        "keys ranked", passed_verification, NPBVERSION, COMPILETIME, CC, CLINK,
        C_LIB, C_INC, CFLAGS, CLINKFLAGS);

    return 0;
}
