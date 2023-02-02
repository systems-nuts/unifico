#include <inttypes.h>
#include <stdio.h>

// int y = 8;
// int z;
// static int v = 10;
// static int w = 11;

int add_7(int a, int b, int c, int d, int e, int f, int g)
{
    int x;
    x = a + b + c + d + e + f + g;
    return x;
}

int main(int argc, char **argv)
{
    int x = add_7(1, 2, 3, 4, 5, 6, 7);
    printf("%d\n", x);
    return 0;
}
