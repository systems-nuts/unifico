#include <stdio.h>

int main()
{
    int i = 0, j;

    while (i < 10) {
        j = 3 * i + 2;
        i = i + 2;
    }

    printf("%d\n", j);
}
