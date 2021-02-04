#include <stdio.h>
#include <inttypes.h>

int add_7(int a, int b, int c, int d,
		  int e, int f, int g)
{
	int x = 0;
	return a + b + c + d + e + f + g;
}

int main(int argc, char **argv) 
{
	printf("%d\n", add_7(1, 2, 3, 4, 5, 6, 7));
    return 0;
}
