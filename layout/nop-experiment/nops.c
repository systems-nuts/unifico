#include <stdio.h>
#include <time.h>

#define nop ({ __asm__ volatile ("nop\n\t" : : : "memory"); })
#define nop2 ({nop; nop;})
#define nop4 ({nop2; nop2;})
#define nop8 ({nop4; nop4;})
#define nop16 ({nop8; nop8;})
#define nop32 ({nop16; nop16;})
#define nop64 ({nop32; nop32;})
#define nop128 ({nop64; nop64;})
#define nop256 ({nop128; nop128;})
#define nop512 ({nop256; nop256;})
#define nop1024 ({nop512; nop512;})

static const unsigned ITERATIONS = 1000000;

double what_time_is_it()
{
	struct timespec now;
	clock_gettime(CLOCK_REALTIME, &now);
	return now.tv_sec + now.tv_nsec*1e-9;
}


int main()
{
	double t0 = what_time_is_it();
	for (int i = 0; i < ITERATIONS; ++i)
		nop;
	printf("nop time: %.6lf\n", what_time_is_it() - t0);

	t0 = what_time_is_it();
	for (int i = 0; i < ITERATIONS; ++i)
		nop2;
	printf("nop2 time: %.6lf\n", what_time_is_it() - t0);

	t0 = what_time_is_it();
	for (int i = 0; i < ITERATIONS; ++i)
		nop4;
	printf("nop4 time: %.6lf\n", what_time_is_it() - t0);

	t0 = what_time_is_it();
	for (int i = 0; i < ITERATIONS; ++i)
		nop8;
	printf("nop8 time: %.6lf\n", what_time_is_it() - t0);

	t0 = what_time_is_it();
	for (int i = 0; i < ITERATIONS; ++i)
		nop16;
	printf("nop16 time: %.6lf\n", what_time_is_it() - t0);

	t0 = what_time_is_it();
	for (int i = 0; i < ITERATIONS; ++i)
		nop32;
	printf("nop32 time: %.6lf\n", what_time_is_it() - t0);

	t0 = what_time_is_it();
	for (int i = 0; i < ITERATIONS; ++i)
		nop64;
	printf("nop64 time: %.6lf\n", what_time_is_it() - t0);

	t0 = what_time_is_it();
	for (int i = 0; i < ITERATIONS; ++i)
		nop128;
	printf("nop128 time: %.6lf\n", what_time_is_it() - t0);

	t0 = what_time_is_it();
	for (int i = 0; i < ITERATIONS; ++i)
		nop256;
	printf("nop256 time: %.6lf\n", what_time_is_it() - t0);

	t0 = what_time_is_it();
	for (int i = 0; i < ITERATIONS; ++i)
		nop512;
	printf("nop512 time: %.6lf\n", what_time_is_it() - t0);

	t0 = what_time_is_it();
	for (int i = 0; i < ITERATIONS; ++i)
		nop1024;
	printf("nop1024 time: %.6lf\n", what_time_is_it() - t0);

	return 0;
}
