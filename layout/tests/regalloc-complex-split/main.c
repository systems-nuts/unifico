#include <stdio.h>

int fmul(int x, int y) { return x * y; }

int loop(int *a1, int len)
{
    int sum = 0;
    for (int i = 0; i < len; i++) {
        sum += fmul(a1[i], a1[i]);
    }
    return sum;
}

int main()
{
    int a1[8];
    loop(a1, 8);
    return 0;
}
