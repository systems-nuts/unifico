#include <stdio.h>
#include <stdlib.h>
// float version of saved
// will cause different spill weights in reg-alloc enqueue

float leaf(float x) { return x + 1; }

float func(float x)
{
    float c1 = leaf(x);
    float c2 = leaf(x * 2);
    float c3 = leaf(x * 3);
    return c1 + c2 + c3;
}

// callee saved register used
// r1 - r6 are saved before func(1)
// $eax are saved for every func() before next one
float saved(float r1, float r2, float r3, float r4, float r5, float r6)
{
    float c1 = func(1);
    float c2 = func(2);
    float c3 = func(3);
    float c4 = func(4);
    float c5 = func(5);
    float c6 = func(6);
    float c7 = func(7);
    float c8 = func(8);
    float c9 = func(9);
    float c10 = func(10);
    float cc = c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + c9 + c10;
    float param = r1 + r2 + r3 + r4 + r5 + r6;
    return param + cc;
}

int main()
{
    printf("%f\n", saved(1, 2, 3, 4, 5, 6));
    return 0;
}
