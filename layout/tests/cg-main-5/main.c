#include <stdio.h>

int main()
{
    int x[10] = {0};
    int nrows = 10, n, m;

    for (int j = 1; j < nrows - 1; j++) {
        n = x[j + 1];
        m = x[j];
    }
    printf("%d\n", x[0]);

    return 0;
}
