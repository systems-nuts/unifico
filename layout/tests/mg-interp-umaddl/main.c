void simple(int n) { return; }

static void interp(void *oz, int mm1, int mm2, int mm3, void *ou, int n1,
                   int n2, int n3);

int main()
{
    double u[10];

    interp(&u[0], 1, 1, 1, &u[0], 1, 1, 1);
}

static void interp(void *oz, int mm1, int mm2, int mm3, void *ou, int n1,
                   int n2, int n3)
{
    int(*z)[mm2][mm1] = (int(*)[mm2][mm1])oz;
    int(*u)[n2][n1] = (int(*)[n2][n1])ou;

    int i3 = 3, i2 = 2, i1 = 1;

    simple(1);
    u[i3][i2][i1] = z[i3][i2][i1];
}
