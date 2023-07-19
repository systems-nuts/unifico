#include <stdio.h>
#include <stdlib.h>

int leaf(int x) { return x + 1; }

// test two callee saved push
// c1 - c3 are saved in callee regs so callee regs are pushed
int func(int x)
{
    int c1 = leaf(x);
    int c2 = leaf(x * 2);
    int c3 = leaf(x * 3);
    return c1 + c2 + c3;
}

// callee saved register used
// r1 - r6 are saved before func(1)
// $eax are saved for every func() before next one
int saved(int r1, int r2, int r3, int r4, int r5, int r6)
{
    int c1 = func(1);
    int c2 = func(2);
    int c3 = func(3);
    int c4 = func(4);
    int c5 = func(5);
    int c6 = func(6);
    int c7 = func(7);
    int c8 = func(8);
    int c9 = func(9);
    int c10 = func(10);
    int cc = c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + c9 + c10;
    int param = r1 + r2 + r3 + r4 + r5 + r6;
    return param / cc;
}

int main()
{
    printf("%d\n", saved(1, 2, 3, 4, 5, 6));
    return 0;
}
