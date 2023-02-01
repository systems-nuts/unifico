#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "globals.h"
#include "randdp.h"
#include "timers.h"

//---------------------------------------------------------------------
/* common / main_int_mem / */
static int colidx[NZ];
static int rowstr[NA + 1];
static int iv[NA];
static int arow[NA];
static int acol[NAZ];

/* common / main_flt_mem / */
static double aelt[NAZ];
static double a[NZ];
static double x[NA + 2];
static double z[NA + 2];
static double p[NA + 2];
static double q[NA + 2];
static double r[NA + 2];

/* common / partit_size / */
static int naa;
static int nzz;
static int firstrow;
static int lastrow;
static int firstcol;
static int lastcol;

/* common /urando/ */
static double amult;
static double tran;

/* common /timers/ */
static logical timeron;
//---------------------------------------------------------------------

//---------------------------------------------------------------------
static void conj_grad(int colidx[], int rowstr[], double x[], double z[],
                      double a[], double p[], double q[], double r[],
                      double *rnorm);
static void makea(int n, int nz, double a[], int colidx[], int rowstr[],
                  int firstrow, int lastrow, int firstcol, int lastcol,
                  int arow[], int acol[][NONZER + 1], double aelt[][NONZER + 1],
                  int iv[]);
static void sparse(double a[], int colidx[], int rowstr[], int n, int nz,
                   int nozer, int arow[], int acol[][NONZER + 1],
                   double aelt[][NONZER + 1], int firstrow, int lastrow,
                   int nzloc[], double rcond, double shift);
static void sprnvc(int n, int nz, int nn1, double v[], int iv[]);
static int icnvrt(double x, int ipwr2);
static void vecset(int n, double v[], int iv[], int *nzv, int i, double val);
//---------------------------------------------------------------------

int main(int argc, char *argv[])
{
    int i, j, k, it;

    double zeta;
    double rnorm;
    double norm_temp1, norm_temp2;

    double t, mflops, tmax;
    char Class;
    logical verified;
    double zeta_verify_value, epsilon, err;

    char *t_names[T_last];

    for (i = 0; i < T_last; i++) {
        timer_clear(i);
    }

    FILE *fp;
    if ((fp = fopen("timer.flag", "r")) != NULL) {
        timeron = true;
        t_names[T_init] = "init";
        t_names[T_bench] = "benchmk";
        t_names[T_conj_grad] = "conjgd";
        fclose(fp);
    }
    else {
        timeron = false;
    }

    timer_start(T_init);

    firstrow = 0;
    lastrow = NA - 1;
    firstcol = 0;
    lastcol = NA - 1;

    if (NA == 1400 && NONZER == 7 && NITER == 15 && SHIFT == 10) {
        Class = 'S';
        zeta_verify_value = 8.5971775078648;
    }
    else if (NA == 7000 && NONZER == 8 && NITER == 15 && SHIFT == 12) {
        Class = 'W';
        zeta_verify_value = 10.362595087124;
    }
    else if (NA == 14000 && NONZER == 11 && NITER == 15 && SHIFT == 20) {
        Class = 'A';
        zeta_verify_value = 17.130235054029;
    }
    else if (NA == 75000 && NONZER == 13 && NITER == 75 && SHIFT == 60) {
        Class = 'B';
        zeta_verify_value = 22.712745482631;
    }
    else if (NA == 150000 && NONZER == 15 && NITER == 75 && SHIFT == 110) {
        Class = 'C';
        zeta_verify_value = 28.973605592845;
    }
    else if (NA == 1500000 && NONZER == 21 && NITER == 100 && SHIFT == 500) {
        Class = 'D';
        zeta_verify_value = 52.514532105794;
    }
    else if (NA == 9000000 && NONZER == 26 && NITER == 100 && SHIFT == 1500) {
        Class = 'E';
        zeta_verify_value = 77.522164599383;
    }
    else {
        Class = 'U';
    }

    printf("\n\n NAS Parallel Benchmarks (NPB3.3-SER-C) - CG Benchmark\n\n");
    printf(" Size: %11d\n", NA);
    printf(" Iterations: %5d\n", NITER);
    printf("\n");

    naa = NA;
    nzz = NZ;

    //---------------------------------------------------------------------
    // Inialize random number generator
    //---------------------------------------------------------------------
    tran = 314159265.0;
    amult = 1220703125.0;
    zeta = randlc(&tran, amult);

    //---------------------------------------------------------------------
    //
    //---------------------------------------------------------------------
    makea(naa, nzz, a, colidx, rowstr, firstrow, lastrow, firstcol, lastcol,
          arow, (int(*)[NONZER + 1])(void *)acol,
          (double(*)[NONZER + 1])(void *)aelt, iv);

    //---------------------------------------------------------------------
    // Note: as a result of the above call to makea:
    //      values of j used in indexing rowstr go from 0 --> lastrow-firstrow
    //      values of colidx which are col indexes go from firstcol --> lastcol
    //      So:
    //      Shift the col index vals from actual (firstcol --> lastcol )
    //      to local, i.e., (0 --> lastcol-firstcol)
    //---------------------------------------------------------------------
    for (j = 0; j < lastrow - firstrow + 1; j++) {
        for (k = rowstr[j]; k < rowstr[j + 1]; k++) {
            colidx[k] = colidx[k] - firstcol;
        }
    }

    //---------------------------------------------------------------------
    // set starting vector to (1, 1, .... 1)
    //---------------------------------------------------------------------
    for (i = 0; i < NA + 1; i++) {
        x[i] = 1.0;
    }
    for (j = 0; j < lastcol - firstcol + 1; j++) {
        q[j] = 0.0;
        z[j] = 0.0;
        r[j] = 0.0;
        p[j] = 0.0;
    }

    zeta = 0.0;

    //---------------------------------------------------------------------
    //---->
    // Do one iteration untimed to init all code and data page tables
    //---->                    (then reinit, start timing, to niter its)
    //---------------------------------------------------------------------
    for (it = 1; it <= 1; it++) {
        //---------------------------------------------------------------------
        // The call to the conjugate gradient routine:
        //---------------------------------------------------------------------
        conj_grad(colidx, rowstr, x, z, a, p, q, r, &rnorm);

        //---------------------------------------------------------------------
        // zeta = shift + 1/(x.z)
        // So, first: (x.z)
        // Also, find norm of z
        // So, first: (z.z)
        //---------------------------------------------------------------------
        norm_temp1 = 0.0;
        norm_temp2 = 0.0;
        for (j = 0; j < lastcol - firstcol + 1; j++) {
            norm_temp1 = norm_temp1 + x[j] * z[j];
            norm_temp2 = norm_temp2 + z[j] * z[j];
        }

        norm_temp2 = 1.0 / sqrt(norm_temp2);

        //---------------------------------------------------------------------
        // Normalize z to obtain x
        //---------------------------------------------------------------------
        for (j = 0; j < lastcol - firstcol + 1; j++) {
            x[j] = norm_temp2 * z[j];
        }
    } // end of do one iteration untimed

    //---------------------------------------------------------------------
    // set starting vector to (1, 1, .... 1)
    //---------------------------------------------------------------------
    for (i = 0; i < NA + 1; i++) {
        x[i] = 1.0;
    }

    zeta = 0.0;

    timer_stop(T_init);

    printf(" Initialization time = %15.3f seconds\n", timer_read(T_init));

    timer_start(T_bench);

    //---------------------------------------------------------------------
    //---->
    // Main Iteration for inverse power method
    //---->
    //---------------------------------------------------------------------
    for (it = 1; it <= NITER; it++) {
        //---------------------------------------------------------------------
        // The call to the conjugate gradient routine:
        //---------------------------------------------------------------------
        // migrate(1, NULL, NULL);
        if (timeron)
            timer_start(T_conj_grad);
        conj_grad(colidx, rowstr, x, z, a, p, q, r, &rnorm);
        if (timeron)
            timer_stop(T_conj_grad);
        // migrate(0, NULL, NULL);

        //---------------------------------------------------------------------
        // zeta = shift + 1/(x.z)
        // So, first: (x.z)
        // Also, find norm of z
        // So, first: (z.z)
        //---------------------------------------------------------------------
        norm_temp1 = 0.0;
        norm_temp2 = 0.0;
        for (j = 0; j < lastcol - firstcol + 1; j++) {
            norm_temp1 = norm_temp1 + x[j] * z[j];
            norm_temp2 = norm_temp2 + z[j] * z[j];
        }

        norm_temp2 = 1.0 / sqrt(norm_temp2);

        zeta = SHIFT + 1.0 / norm_temp1;
        if (it == 1)
            printf("\n   iteration           ||r||                 zeta\n");
        printf("    %5d       %20.14E%20.13f\n", it, rnorm, zeta);

        //---------------------------------------------------------------------
        // Normalize z to obtain x
        //---------------------------------------------------------------------
        for (j = 0; j < lastcol - firstcol + 1; j++) {
            x[j] = norm_temp2 * z[j];
        }
    } // end of main iter inv pow meth

    timer_stop(T_bench);

    //---------------------------------------------------------------------
    // End of timed section
    //---------------------------------------------------------------------

    t = timer_read(T_bench);

    printf(" Benchmark completed\n");

    epsilon = 1.0e-10;
    if (Class != 'U') {
        err = fabs(zeta - zeta_verify_value) / zeta_verify_value;
        if (err <= epsilon) {
            verified = true;
            printf(" VERIFICATION SUCCESSFUL\n");
            printf(" Zeta is    %20.13E\n", zeta);
            printf(" Error is   %20.13E\n", err);
        }
        else {
            verified = false;
            printf(" VERIFICATION FAILED\n");
            printf(" Zeta                %20.13E\n", zeta);
            printf(" The correct zeta is %20.13E\n", zeta_verify_value);
        }
    }
    else {
        verified = false;
        printf(" Problem size unknown\n");
        printf(" NO VERIFICATION PERFORMED\n");
    }

    if (t != 0.0) {
        mflops = (double)(2 * NITER * NA) *
                 (3.0 + (double)(NONZER * (NONZER + 1)) +
                  25.0 * (5.0 + (double)(NONZER * (NONZER + 1))) + 3.0) /
                 t / 1000000.0;
    }
    else {
        mflops = 0.0;
    }

    print_results("CG", Class, NA, 0, 0, NITER, t, mflops,
                  "          floating point", verified, NPBVERSION, COMPILETIME,
                  CS1, CS2, CS3, CS4, CS5, CS6, CS7);

    //---------------------------------------------------------------------
    // More timers
    //---------------------------------------------------------------------
    if (timeron) {
        tmax = timer_read(T_bench);
        if (tmax == 0.0)
            tmax = 1.0;
        printf("  SECTION   Time (secs)\n");
        for (i = 0; i < T_last; i++) {
            t = timer_read(i);
            if (i == T_init) {
                printf("  %8s:%9.3f\n", t_names[i], t);
            }
            else {
                printf("  %8s:%9.3f  (%6.2f%%)\n", t_names[i], t,
                       t * 100.0 / tmax);
                if (i == T_conj_grad) {
                    t = tmax - t;
                    printf("    --> %8s:%9.3f  (%6.2f%%)\n", "rest", t,
                           t * 100.0 / tmax);
                }
            }
        }
    }

    return 0;
}

//---------------------------------------------------------------------
// Floaging point arrays here are named as in NPB1 spec discussion of
// CG algorithm
//---------------------------------------------------------------------
static void conj_grad(int colidx[], int rowstr[], double x[], double z[],
                      double a[], double p[], double q[], double r[],
                      double *rnorm)
{
    return;
}

//---------------------------------------------------------------------
// generate the test problem for benchmark 6
// makea generates a sparse matrix with a
// prescribed sparsity distribution
//
// parameter    type        usage
//
// input
//
// n            i           number of cols/rows of matrix
// nz           i           nonzeros as declared array size
// rcond        r*8         condition number
// shift        r*8         main diagonal shift
//
// output
//
// a            r*8         array for nonzeros
// colidx       i           col indices
// rowstr       i           row pointers
//
// workspace
//
// iv, arow, acol i
// aelt           r*8
//---------------------------------------------------------------------
static void makea(int n, int nz, double a[], int colidx[], int rowstr[],
                  int firstrow, int lastrow, int firstcol, int lastcol,
                  int arow[], int acol[][NONZER + 1], double aelt[][NONZER + 1],
                  int iv[])
{
    return;
}
