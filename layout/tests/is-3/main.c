#include <stdio.h>

void rank(int n) { printf("%d\n", n); }

int add_one(int n) { return n + 1; }

int main(int argc, char **argv)
{

    int i = 1, iteration, x;

    rank(4);

    for (iteration = 4; iteration <= 10; iteration++) {
        if (iteration == 0) {
            printf("\n");
        }
    }

    rank(0);
    x = add_one(0);

    if (!iteration)
        rank(2);

    return 0;
}
