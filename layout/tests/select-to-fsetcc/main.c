#include "npbparams.h"
#include <stdio.h>

void timer_clear(int n);
void timer_start(int n);
void timer_stop(int n);
double timer_read(int n);

int main(int argc, char **argv)
{
    volatile int timer_on;
    double timecounter;

    /*  Print additional timers  */
    double t_total, t_percent;
    t_total = timer_read(3);
    printf(" Total execution: %8.3f\n", t_total);
    if (t_total == 0.0)
        t_total = 1.0;
    timecounter = timer_read(1);
    t_percent = timecounter / t_total * 100.;
    printf(" Initialization : %8.3f (%5.2f%%)\n", timecounter, t_percent);
    return 0;
}
