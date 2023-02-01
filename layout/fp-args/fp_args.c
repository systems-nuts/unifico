#include <stdio.h>
// test argument pass for float and double
// ARM and X86 have same behavior

float arg1(float f1, float f2, float f3) { return f1 + f2 + f3; }

float arg2(float f1, float f2, float f3, float f4, float f5, float f6, float f7,
           float f8, float f9)
{
    return f1 + f2 + f3 + f4 + f5 + f6 + f7 + f8 + f9;
}

double arg3(double f1, double f2, double f3) { return f1 + f2 + f3; }

double arg4(double f1, double f2, double f3, double f4, double f5, double f6,
            double f7, double f8, double f9)
{
    return f1 + f2 + f3 + f4 + f5 + f6 + f7 + f8 + f9;
}

int main()
{
    float f1 = arg1(1, 2, 3);
    float f2 = arg2(4, 5, 6, 7, 8, 9, 10, 11, 12);
    double d1 = arg3(1, 2, 3);
    double d2 = arg4(4, 5, 6, 7, 8, 9, 10, 11, 12);
    printf("%f", f1 + f2 + d1 + d2);
    return 0;
}
