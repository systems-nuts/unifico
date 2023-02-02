#include <stdio.h>

#include "npbparams.h"

double timer_read(int n) { return 0.0; }

int main(int argc, char **argv)
{
    int timer_on;
    double timecounter = 0.0;

    if (timer_on) {
        double t_percent;

        timecounter = timer_read(1);
        t_percent = timecounter * 100.;
        printf(" Initialization : %8.3f (%5.2f%%)\n", timecounter, t_percent);
        timecounter = timer_read(2);
        t_percent = timecounter * 100.;
        printf(" Sorting        : %8.3f (%5.2f%%)\n", timecounter, t_percent);
    }

    return 0;
}
