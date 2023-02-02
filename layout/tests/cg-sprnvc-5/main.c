typedef enum { false, true } logical;

static double amult;
static double tran;

double randlc(double *a, double b)
{
    *a++;
    return b++;
}

static int icnvrt(double x, int ipwr2) { return 1; }

static void sprnvc(int n, int nz, int nn1, double v[], int iv[])
{
    int nzv, ii, i;
    double vecelt, vecloc;

    nzv = 0;

    while (nzv < nz) {
        vecelt = randlc(&tran, amult);

        //---------------------------------------------------------------------
        // generate an integer between 1 and n in a portable manner
        //---------------------------------------------------------------------
        vecloc = randlc(&tran, amult);
        i = icnvrt(vecloc, nn1) + 1;
        if (i > n)
            continue;

        //---------------------------------------------------------------------
        // was this integer generated already?
        //---------------------------------------------------------------------
        logical was_gen = false;
        for (ii = 0; ii < nzv; ii++) {
            if (iv[ii] == i) {
                was_gen = true;
                break;
            }
        }
        if (was_gen)
            continue;
        v[nzv] = vecelt;
        iv[nzv] = i;
        nzv = nzv + 1;
    }
}

int main()
{
    double x[10];
    int y[10];
    sprnvc(0, 0, 0, x, y);
    return 0;
}