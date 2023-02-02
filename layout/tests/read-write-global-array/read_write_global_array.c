#include <stdio.h>
#define SIZE 10

int global[SIZE];

int get_array(int index) { return global[index + 3]; }

int main()
{
    for (int i = 0; i < SIZE; i++) {
        global[i] = 2 * i + 10;
    }
    printf("%d\n", get_array(3));
    return 0;
}
