#include <stdio.h>

double a1;
double a2;

double mul(double x, double y) { return a1 * a2 * x * y; }

int main()
{
    a1 = 12345.0;
    a2 = 54321.0;
    printf("%f\n", mul(a1, a2));
    return 0;
}
