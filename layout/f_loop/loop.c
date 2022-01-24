#include <stdio.h>

double fmul(double* x, double* y) {
	static double r = 0.5;
	r += 0.5;
	return (*x) * (*y) * r;
}

// a loop with funciton call inside it
double loop(double x, double y) {
	double sum = 0;
	for (int i = 0; i < 16; i++) {
		sum = fmul(&x, &y);
		sum += fmul(&x, &y);
		sum += fmul(&x, &y);
		sum += fmul(&x, &y);
	}
	return sum;
}

int main()
{
	double res = loop(3.5, 4.5);
	printf("%f", res);
	return 0;
}
