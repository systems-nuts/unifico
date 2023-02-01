#include <stdio.h>

#define A 1220703126.0

double mul(double x, double y) { return x * y; }

int main()
{
    double res, temp;

    temp = A;
    res = mul(temp, temp);
    printf("%f/n", res);
    return 0;
}
