#include <stdio.h>
#include <inttypes.h>

int add_9(int a, int b, int c, int d,
		  int e, int f, int g, int h,
		  int i)
{
	return a + b + c + d + e + f + g + h + i;
}

int main(int argc, char **argv) 
{
	printf("%d\n", add_9(1, 1, 1, 1, 1, 1, 1, 1, 1));
    return 0;
}
