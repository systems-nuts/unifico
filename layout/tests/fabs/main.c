#include <math.h>
#include <stdio.h>

void results(char Class, double epsilon)
{
    double err;
    double zeta_verify_value = 22.712745482631;

    if (Class != 'U') {
        err = fabs(epsilon - zeta_verify_value) / zeta_verify_value;
    }
    err += fabs(epsilon - zeta_verify_value);
    printf(" Error is   %20.14E\n", err);
    return;
}

int main()
{
    results('S', 1.0);

    return 0;
}
