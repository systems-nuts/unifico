#include <stdio.h>

int bar(int x) { return x * x; }

int foo(int x) { return bar(x); }

int main()
{
    int x = 3;
    x = foo(x);
    printf("%d\n", x);
    return 0;
}
