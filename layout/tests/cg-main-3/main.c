#include <stdio.h>

void simple(int n) { return; }

int main()
{
    int t_names[4];
    double t;

    for (int i = 0; i < 10; i++) {
        printf("  %8s:\n", t_names[i]);
    }

    return 0;
}
