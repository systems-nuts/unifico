#include <math.h>
#include <stdio.h>

int main()
{
    double x = 66.6;
    long long y;
    y = llround(x);
    printf("%f %lld\n", x, y);
}
