#include <stdio.h>
#include <stdlib.h>

int cal(int r1, int r2, int r3, int r4, int r5, int r6)
{
    int m1 = r1 * r2 + r3;
    int m2 = r2 * r3 + r4;
    int m3 = r3 * r4 + r5;
    int m4 = r4 * r5 + r1;
    int m5 = r5 * r6 + r1;
    int m6 = r6 * r1 + r2;
    int mm1 = m1 * m2 + m3;
    int mm2 = m2 * m3 + m4;
    int mm3 = m3 * m4 + m5;
    int mm4 = m4 * m5 + m1;
    int mm5 = m5 * m6 + m1;
    int mm6 = m6 * m1 + m2;

    int add_r = r1 + r2 + r3 + r4 + r5 + r6;
    int add_m = m1 + m2 + m3 + m4 + m5 + m6;
    int add_mm =
        m1 * mm1 + m2 * mm2 + m3 * mm3 + m4 * mm4 + m5 * mm5 + m6 * mm6;
    return add_r + add_m + add_mm;
}

int main()
{
    printf("%d\n", cal(1, 2, 3, 4, 5, 6));
    return 0;
}
