#include <stdio.h>

int mul(int x) { return x * x; }

int add_6(int arg1, int arg2, int arg3, int arg4, int arg5, int arg6)
{
    int res1 = mul(1);
    int res2 = mul(2);
    int res3 = mul(3);
    int res4 = mul(4);
    int res5 = mul(5);
    int res6 = mul(6);
    int res7 = mul(7);
    int res8 = mul(8);
    int res9 = mul(9);
    int res10 = mul(10);

    int res_sum =
        res1 + res2 + res3 + res4 + res5 + res6 + res7 + res8 + res9 + res10;
    int arg_sum = arg1 + arg2 + arg3 + arg4 + arg5 + arg6;

    return res_sum + arg_sum;
}

int main()
{
    printf("%d\n", add_6(1, 2, 3, 4, 5, 6));
    return 0;
}
