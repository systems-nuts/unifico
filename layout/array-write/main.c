#include <stdio.h>
#include <stdlib.h>

#define N 1000

void swap(int v[], int k)
{
    int temp;
    temp = v[k];
    v[k] = v[k + 1];
    v[k + 1] = temp;
}

void sort(int v[], int n)
{
    int i, j;
    for (i = 0; i < n; i += 1) {
        for (j = i - 1; j >= 0 && v[j] > v[j + 1]; j -= 1) {
            swap(v, j);
        }
    }
    for (i = n; i > 0; i -= 1) {
        for (j = i - 1; j >= 0 && v[j] > v[j + 1]; j -= 1) {
            swap(v, j);
        }
    }
}

int main()
{
    int *v = (int *)malloc(N * sizeof(int));

    sort(v, N);

    for (int i = 0; i < N; ++i)
        printf("v[%d]=%d\n", i, v[i]);

    return 0;
}
