#include <stdio.h>

void rank(int n) { printf("%d\n", n); }

int main(int argc, char **argv)
{

    int i, iteration;

    rank(4);

    for (iteration = 4; iteration <= 10; iteration++) {
        if (iteration == 0) {
            printf("\n");
        }
    }

    return 0;
}
