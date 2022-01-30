#include <stdio.h>

#define A 1.1

double mul(double x, double y) {
	return x * y;
}

int main()
{
	double c1, c2, t;

	t = A;
	c1 = mul(t, t);
	c2 = c1;
	printf("%f\n", c1 + c2);
	return 0;
}
