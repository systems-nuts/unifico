#include <stdio.h>

#define N 100000

static int colidx[N];
static int rowstr[N];
static double a[N];
static double p[N];
static double q[N];

void matrix_multiplication(int colidx[N], int rowstr[N], double a[N],
                           double p[N], double q[N])
{
    int i, j, k;
    double sum;

    for (j = 0; j < N; j++) {
        colidx[j] = rowstr[j] = j;
        a[j] = p[j] = q[j] = j;
    }

    for (i = 0; i < 10000; i++) {
        for (j = 0; j < N - 1; j++) {
            sum = 0.0;
            for (k = rowstr[j]; k < rowstr[j + 1]; k++) {
                sum = sum + a[k] * p[colidx[k]];
            }
            q[j] = sum;
        }
    }
    printf("%lf\n", q[2]);

    return;
}

int main()
{
    matrix_multiplication(colidx, rowstr, a, p, q);

    return 0;
}
