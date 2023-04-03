#include <inttypes.h>
#include <stdio.h>

int add_4(int a, int b, int c, int d) { return a + b + c + d; }
int add_5(int a, int b, int c, int d, int e) { return a + b + c + d + e; }

int add_9(int a, int b, int c, int d, int e, int f, int g, int h, int i)
{
    return add_4(a, b, c, d) + add_5(e, f, g, h, i);
}

int main(int argc, char **argv)
{
    printf("%d\n", add_9(1, 2, 3, 4, 5, 6, 7, 8, 9));
    return 0;
}
