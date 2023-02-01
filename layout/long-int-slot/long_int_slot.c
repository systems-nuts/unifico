#include <stdio.h>

long int mul(long int x) { return x * x; }

int main()
{
    long int c1;

    c1 = mul(3);
    printf("%f\n", c1);
    return 0;
}
