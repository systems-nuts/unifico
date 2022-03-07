#include <stdio.h>


int main()
{
    int i = 0, j;
    int a[100];

    while(i < 10)
    {
      j = 3 * i + 2;
      a[j] = a[j] - 2;
      i = i + 2;
    }

    printf("%d\n", j);
}
