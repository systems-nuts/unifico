double amult;

void randlc(double a) { a++; }

void randlc_ptr(double *a) { a = 5; }

static void sprnvc()
{
    amult = 12345.0;
    while (1) {
        randlc(amult);
    }
}

int main()
{
    sprnvc();
    return 0;
}