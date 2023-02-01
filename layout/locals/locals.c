#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main()
{
    srand(time(NULL));

    int a[25];

    for (int i = 0; i < 25; ++i)
        a[i] = rand() % 100;

    for (int i = 0; i < 25; ++i)
        printf("%d ", a[i]);

    printf("\n");

    return 0;
}
