#include <stdio.h>

#define A 1220703125.0

double mul(double x, double y) {
	return x * y;
}

double div(double x, double y) {
	return x / y;
}

#define A 1220703125.0
int main()
{
	double c1, c2, t;

	t = A;
	c1 = mul(t, t);
	c2 = div(t, t);
	printf("%f/n", c1 + c2);
	return 0;
}
