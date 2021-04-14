#include <stdio.h>

// %rbx is used strangely here.
// it gets from popq the result from the previous call to fact.
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
	printf("fact(4)= %d\n", fact(4));
	return 0;
}
