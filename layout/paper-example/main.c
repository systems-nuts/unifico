#include <stdio.h>

double fmul(double *x)
{
    static double r = 0.5;
    return (*x) * r;
}

int main()
{
    double x = 1.0;
    double sum = 0;
    for (int i = 0; i < 16; i++) {
        sum = fmul(&x);
    }
    printf("%f", sum);
    return 0;
}