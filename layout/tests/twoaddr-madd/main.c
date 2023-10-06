#include <stdio.h>

void results(char *name, int n1, int n2, int n3)
{
    long nn = n1;
    if (n2 != 0)
        nn *= n2;
    printf("%ld%d%4d\n", nn, n1, n2);
}

int main()
{
    results("IS", 1, 64, 0);
    return 0;
}
