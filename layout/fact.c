#include <stdio.h>

int fact(int n)
{
	if (n < 1) {
		int x = 0;
		return 1;
	}
	else {
		int x = 1;
		return n * fact(n - 1);
	}
}

int main()
{
	printf("fact(10)= %d\n", fact(10));
}
