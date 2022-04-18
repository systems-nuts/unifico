#include <stdio.h>

#define  MAX_KEY_LOG_2       21
#define  MAX_KEY             (1 << MAX_KEY_LOG_2)

#define  TOTAL_KEYS_LOG_2    25
#define  TOTAL_KEYS          (1 << TOTAL_KEYS_LOG_2)
#define  NUM_KEYS            TOTAL_KEYS

#define  SIZE_OF_BUFFERS     NUM_KEYS


int key_array[SIZE_OF_BUFFERS];


double randlc(double *X, double *A)
{
      static int        KS=0;
      static double	R23, R46, T23, T46;
      double		T1, T2, T3, T4;
      double		A1;
      double		A2;
      double		X1;
      double		X2;
      double		Z;
      int     		i, j;

      if (KS == 0)
      {
        R23 = 1.0;
        R46 = 1.0;
        T23 = 1.0;
        T46 = 1.0;

        for (i=1; i<=23; i++)
        {
          R23 = 0.50 * R23;
          T23 = 2.0 * T23;
        }
        for (i=1; i<=46; i++)
        {
          R46 = 0.50 * R46;
          T46 = 2.0 * T46;
        }
        KS = 1;
      }

/*  Break A into two parts such that A = 2^23 * A1 + A2 and set X = N.  */

      T1 = R23 * *A;
      j  = T1;
      A1 = j;
      A2 = *A - T23 * A1;

/*  Break X into two parts such that X = 2^23 * X1 + X2, compute
    Z = A1 * X2 + A2 * X1  (mod 2^23), and then
    X = 2^23 * Z + A2 * X2  (mod 2^46).                            */

      T1 = R23 * *X;
      j  = T1;
      X1 = j;
      X2 = *X - T23 * X1;
      T1 = A1 * X2 + A2 * X1;

      j  = R23 * T1;
      T2 = j;
      Z = T1 - T23 * T2;
      T3 = T23 * Z + A2 * X2;
      j  = R46 * T3;
      T4 = j;
      *X = T3 - T46 * T4;
      return(R46 * *X);
}


void create_seq( double seed, double a )
{
	double x;
	int i, k;

    k = MAX_KEY/4;

	for (i=0; i<NUM_KEYS; i++)
	{
	    x = randlc(&seed, &a);
	    x += randlc(&seed, &a);
    	x += randlc(&seed, &a);
	    x += randlc(&seed, &a);

        key_array[i] = k*x;
	}
}


int main()
{
    create_seq(3.0, 4.0);
	return 0;
}
