#include <stdio.h>

void results(char *name, char class, int n1, int n2, int n3, niter,
             char *optype)
{
    if (n3 == 0) {
        long nn = n1;
        if (n2 != 0)
            nn *= n2;
        printf("%ld\n", nn);
    }
    else
        printf("%d%d%d\n", n1, n2, n3);

    printf("%s\n", optype);
}

int main()
{
    results("IS", 'S', 1, 64, 0, 3, "keys ranked");

    return 0;
}
