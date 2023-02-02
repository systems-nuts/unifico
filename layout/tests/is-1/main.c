#include <stdio.h>

int main(int argc, char **argv)
{

    int i, iteration;

    for (iteration = 1; iteration <= 10; iteration++) {
        if (iteration == 0) {
            iteration++;
            printf("\n");
        }
        printf("\n");
    }

    return 0;
}
