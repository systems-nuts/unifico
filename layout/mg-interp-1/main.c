void simple(int n)
{
    return;
}

static void interp(void *oz, int m1, int m2, int m3,
                   void *ou, int n1, int n2, int n3);

int main()
{
    double u[10];

    interp(&u[0], 1, 1, 1, &u[0], 1, 1, 1);
}

static void interp(void *oz, int m1, int m2, int m3,
                   void *ou, int n1, int n2, int n3)
{
  int (*z)[m2][m3] = (int (*)[m2][m3])oz;
  int (*u)[n2][n3] = (int (*)[n2][n3])ou;

  int i3 = 3, i2 = 2, i1 = 1;

  simple(1);
  for (i3 = 0; i3 < m3-1; i3++) {
    u[i1][i2][i3] = z[i1][i2][i3];
  }
}
