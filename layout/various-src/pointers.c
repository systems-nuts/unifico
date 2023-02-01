int foo(int a, int b) { return a + b; }

int main()
{
    foo(1, 2);
    int x = 4;
    int *y = &x;
    int z = *y;

    struct {
        int a;
        int b;
    } c[10];
    int *p = &c[2].b;
    return 0;
}