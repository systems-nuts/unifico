#include <stdio.h>

double fmul(double *x, double *y)
{
    static double r = 0.5;
    r += 0.5;
    return (*x) * (*y) * r;
}

int main()
{
    double x = 3.5;
    double y = 4.5;
    double sum = 0;
    for (int i = 0; i < 16; i++) {
        sum = fmul(&x, &y);
        sum += fmul(&x, &y);
    }
    printf("%f", sum);
    return 0;
}
