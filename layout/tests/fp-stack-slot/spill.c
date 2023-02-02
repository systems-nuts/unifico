#include <stdio.h>

float func(float f) { return f * f; }

float spill()
{
    float f1 = func(1);
    float f2 = func(2);
    float f3 = func(3);
    float f4 = func(4);
    float fa1 = f1 + f2;
    float fa2 = f3 + f4;
    float ff1 = func(fa1);
    float ff2 = func(fa2);
    float ffa = func(ff1 + ff2);
    return f1 + f2 + f3 + f4 + fa1 + fa2 + ffa;
}

int main()
{
    float ff = spill();
    printf("%f", ff);
    return 0;
}
