#include <math.h>
#include <stdio.h>
#include <stdlib.h>

double randlc(double *a, double b) { return 0.0; }

int main()
{
    double dum[3] = {1.0, 1.0, 1.0};

    dum[0] = randlc(&dum[1], dum[2]);
    dum[0] = randlc(&dum[1], dum[2]);

    return 0;
}
