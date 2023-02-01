#include <stdio.h>

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
}

int main()
{
    int v[5] = {4, 1, 3, 2, 1};

    sort(v, 5);

    for (int i = 0; i < 5; ++i)
        printf("v[%d]=%d\n", i, v[i]);

    return 0;
}
