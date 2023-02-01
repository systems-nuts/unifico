#include <stdio.h>

#define TOTAL_KEYS_LOG_2 25
#define TOTAL_KEYS (1L << TOTAL_KEYS_LOG_2)
#define MAX_ITERATIONS 10

int main(int argc, char **argv)
{
    double timecounter = 4.0;
    printf("%lf, %lf\n", timecounter,
           ((double)(MAX_ITERATIONS * TOTAL_KEYS)) / timecounter / 1000000.);

    timecounter = 0.0;
    printf("%lf, %lf\n", timecounter,
           ((double)(MAX_ITERATIONS * TOTAL_KEYS)) / timecounter / 1000000.);

    return 0;
}
