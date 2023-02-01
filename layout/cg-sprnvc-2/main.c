double amult;

void randlc(double a) { a++; }

static void sprnvc()
{
    while (1) {
        randlc(amult);
        randlc(amult);
    }
}

int main()
{
    sprnvc();
    return 0;
}