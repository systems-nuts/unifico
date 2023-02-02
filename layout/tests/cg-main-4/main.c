#include <stdio.h>

int main()
{
    int t_names[4];
    double t;

    for (int i = 0; i < 10; i++) {
        if (i == 5) {
            printf("  %8s:\n", t_names[i]);
        }
        else {
            printf("  %8s:%9.3f  (%6.2f%%)\n", t_names[i], t, 100.0);
        }
    }

    return 0;
}
