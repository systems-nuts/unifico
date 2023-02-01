#include <stdio.h>

#define N 16

double x[10];

int main()
{
    double n, m;

    for (int i = 0; i < N; i++) {
        n = 2.0 * x[2 * i] - 1.0;
        m = 2.0 * x[2 * i + 1] - 1.0;
        n = n * n + m * m;
    }
    printf("%lf\n", x[0]);

    return 0;
}
