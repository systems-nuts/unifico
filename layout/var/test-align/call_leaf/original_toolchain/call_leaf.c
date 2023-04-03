#include <inttypes.h>
#include <stdio.h>

int y = 8;
int z;
static int v = 10;
static int w = 11;
static int o = 11;

int add_7(int a, int b, int c, int d, int e, int f, int g)
{
    int x;
    z = 9;
    x = a + b + c + d + e + f + g + y + z + v + w + o;
    return x;
}

int main(int argc, char **argv)
{
    printf("%d\n", add_7(1, 2, 3, 4, 5, 6, 7));
    printf("boom\n");
    return 0;
}
