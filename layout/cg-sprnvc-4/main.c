void simple() { return; }

static void sprnvc()
{
    while (1) {
        simple();
        int x = 0;
        x = x + 2;
    }
}

int main()
{
    sprnvc();
    return 0;
}