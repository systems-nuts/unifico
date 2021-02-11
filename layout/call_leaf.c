#include <stdio.h>
#include <inttypes.h>

static int variable_1 = 0;
static int variable_2 = 777;

int add_7(int a, int b, int c, int d,
		  int e, int f, int g)
{
	int x;
	x =  a + b + c + d + e + f + g;
	return x;
}

int main(int argc, char **argv) 
{
	printf("%d\n", add_7(1, 2, 3, 4, 5, 6, 7));
	printf("boom\n");
	printf("%d%d\n", variable_1, variable_2);
    return 0;
}
