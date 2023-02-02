#include <stdio.h>

#define NX 512
#define NY 256

static double twiddle[NX][NY + 1];

double simple(double n) { return n; }

int main()
{
    int i;

    while (1)
        twiddle[i][i] = simple((double)(i));
}
