#include <stdio.h>

#define NA 75000
#define NONZER 13
#define NZ (NA * (NONZER + 1) * (NONZER + 1))
#define NAZ (NA * (NONZER + 1))

static int naa;
static int nzz;

void simple(int n) { return; }

int main()
{
    int x, y;
    x = NA - 1;
    printf("\n");
    y = NA;

    printf(" Size: %11d\n", NA);

    naa = NA;
    nzz = NZ;

    printf("\n");

    return 0;
}
