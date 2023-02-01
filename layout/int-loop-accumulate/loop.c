#include <stdio.h>

// a simple for loop

int mul(int x, int y) { return x * y; }

int main()
{
    int sum = 0;
    for (int i = 0; i < 10; i++) {
        sum += mul(i, i + 1);
    }
    printf("%d", sum);
    return 0;
}
