#include "type.h"

void simple() { return; }

static void Swarztrauber(int xd1, void *ox)
{
    dcomplex(*x)[xd1] = (dcomplex(*)[xd1])ox;

    int i = 5, k = 2, m = 3;
    dcomplex x11;

    simple();

    x11 = x[i][k];
}

int main()
{
    void *p;
    Swarztrauber(1, p);
}
