#include "randdp.h"
#include "type.h"

#define MAXDIM 512

//---------------------------------------------------------------------
// compute a^exponent mod 2^46
//---------------------------------------------------------------------
static double ipow46(double a, int exponent)
{
    double result, dummy, q, r;
    int n, n2;

    //---------------------------------------------------------------------
    // Use
    //   a^n = a^(n/2)*a^(n/2) if n even else
    //   a^n = a*a^(n-1)       if n odd
    //---------------------------------------------------------------------
    result = 1;
    if (exponent == 0)
        return result;
    q = a;
    r = 1;
    n = exponent;

    while (n > 1) {
        n2 = n / 2;
        if (n2 * 2 == n) {
            dummy = randlc(&q, q);
            n = n2;
        }
        else {
            dummy = randlc(&r, q);
            n = n - 1;
        }
    }
    dummy = randlc(&r, q);
    result = r;
    return result;
}

void compute_initial_conditions(int d1, int d2, int d3,
                                dcomplex u0[d3][d2][d1 + 1])
{
    dcomplex tmp[MAXDIM];
    double x0, start, an, dummy;
    double RanStarts[MAXDIM];

    int i, j, k;
    const double seed = 314159265.0;
    const double a = 1220703125.0;

    start = seed;
    //---------------------------------------------------------------------
    // Jump to the starting element for our first plane.
    //---------------------------------------------------------------------
    an = ipow46(a, 0);
    dummy = randlc(&start, an);
    an = ipow46(a, 2 * d1 * d2);
    //---------------------------------------------------------------------
    // Go through by z planes filling in one square at a time.
    //---------------------------------------------------------------------
    RanStarts[0] = start;
    for (k = 1; k < d3; k++) {
        dummy = randlc(&start, an);
        RanStarts[k] = start;
    }

    for (k = 0; k < d3; k++) {
        x0 = RanStarts[k];
        for (j = 0; j < d2; j++) {
            vranlc(2 * d1, &x0, a, (double *)tmp);
            for (i = 0; i < d1; i++) {
                u0[k][j][i] = tmp[i];
            }
        }
    }
}

int main()
{
    dcomplex u0[10][10][10];
    compute_initial_conditions(0, 0, 0, u0);
}