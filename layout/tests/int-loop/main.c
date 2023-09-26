#include <stdio.h>

int fmul(int x, int y) { return x * y; }

int loop(int *a1, int *a2, int len)
{
    int sum = 0;
    for (int i = 0; i < len; i++) {
        sum += fmul(a1[i], a2[i]);
    }
    return sum;
}

int main()
{
    int a1[8];
    int a2[8];
    for (size_t i = 0; i < 8; i++) {
        a1[i] = 2 * i + 1;
        a2[i] = 3 * i - 1;
    }
    int r1 = loop(a1, a2, 8);
    printf("%d", r1);
    return 0;
}
