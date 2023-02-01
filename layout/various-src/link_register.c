#include <inttypes.h>
#include <stdio.h>

int double_self(int a) { return a + a; }

int intermediate(int a) { return double_self(a); }

int main(int argc, char **argv)
{
    printf("%d\n", intermediate(1));
    return 0;
}
