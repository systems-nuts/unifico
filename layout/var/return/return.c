#include <stdio.h>

struct struct_A {
    int i0;
    int i1;
    double d0;
    double d1;
} AA;

struct struct_A func(int i0, int i1, int i2, int i3, int i4, int i5, double d0,
                     double d1)
{
    struct struct_A A1;
    A1.i0 = i0 + i1 + i2;
    A1.i1 = i3 + i4 + i5;
    A1.d0 = d0;
    A1.d1 = d1;
    return A1;
}

int main()
{
    AA = func(1, 2, 3, 4, 5, 6, 1.0, 2.0);
    return 0;
}
