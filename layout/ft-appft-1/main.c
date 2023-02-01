#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "global.h"

static double twiddle[NZ][NY][NX + 1];

double simple(double n) { return n; }

int main()
{
    int i, j, k;

    for (i = 0; i < 10; i++) {
        for (k = 0; k < 10; k++) {
            for (j = 0; j < 10; j++) {
                twiddle[i][k][j] = simple((double)(j));
            }
        }
    }
}
