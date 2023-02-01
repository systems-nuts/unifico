#include <stdio.h>

int global_array[30];

int main()
{
    int x = 3;
    global_array[x] = 5;
    for (int i = 0; i < 10; i++) {
        printf("%d\n", global_array[x * i]);
    }
    return 0;
}
