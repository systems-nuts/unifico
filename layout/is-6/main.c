#include <stdio.h>


double timer_read(int n)
{
    return 0.0;
}


int main( int argc, char **argv )
{
    int timer_on;
    double timecounter = 3.0;
    double t_percent = 4.0;

    timecounter = timer_read(1);
    t_percent = timecounter * 101.0;
    timecounter = timer_read(2);
    t_percent = timecounter * 101.0;

    return 0;
}
