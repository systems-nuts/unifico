#include <stdio.h>

void results(char *name, int n1, int n2, int n3)
{
    printf("%s\n", name);

    if (n3 == 0) {
        long nn = n1;
        if (n2 != 0)
            nn *= n2;
        printf("%ld\n", nn);
    }
    else
        printf("%4dx%4dx\n", n1, n2);
}

int main()
{
    results("IS", 1, 64, 0);

    return 0;
}
