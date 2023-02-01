#include <stdio.h>

// %rbx is used strangely here.
// it gets from popq the result from the previous call to fact.
int fact(int n)
{
    if (n < 1) {
        return 1;
    }
    else {
        return n * fact(n - 1);
    }
}

int main()
{
    printf("fact(5)= %d\n", fact(5));
    return 0;
}
