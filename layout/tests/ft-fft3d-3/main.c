#include "type.h"

#define dcmplx_add(a, b)                                                       \
    (dcomplex) { (a).real + (b).real, (a).imag + (b).imag }
#define dcmplx_sub(a, b)                                                       \
    (dcomplex) { (a).real - (b).real, (a).imag - (b).imag }
#define dcmplx_mul(a, b)                                                       \
    (dcomplex)                                                                 \
    {                                                                          \
        ((a).real * (b).real) - ((a).imag * (b).imag),                         \
            ((a).real * (b).imag) + ((a).imag * (b).real)                      \
    }

static dcomplex scr[10][11];
logical timers_enabled;

void simple(int n) { return; }

static void Swarztrauber(int is, int m, int vlen, int n, int xd1, void *ox,
                         dcomplex exponent[n])
{
    dcomplex(*x)[xd1] = (dcomplex(*)[xd1])ox;

    int i, j, l;
    dcomplex u1, x11, x21;
    int k, n1, li, lj, lk, ku, i11, i12, i21, i22;

    simple(4);
    for (l = 1; l <= m; l += 2) {
        x11 = x[i11 + k][l];
        scr[i21 + k][j] = dcmplx_add(x11, x21);
        scr[i22 + k][j] = dcmplx_mul(u1, dcmplx_sub(x11, x21));
    }
}

int main()
{
    void *p;
    dcomplex exp1[10];
    Swarztrauber(1, 1, 1, 1, 1, p, exp1);
}
