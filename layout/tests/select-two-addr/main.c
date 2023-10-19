
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

int main()
{
    lastrow = NA - 1;
    lastcol = NA - 1;

    printf(" Size: %11d\n", NA);

    naa = NA;
    nzz = NZ;
    randlc(&tran, amult);

    makea(naa, nzz, a, colidx, rowstr, 0, lastrow, 0, lastcol, arow,
          (int(*)[NONZER + 1])(void *)acol, (double(*)[NONZER + 1])(void *)aelt,
          iv);

    return 0;
}

static void conj_grad(int colidx[], int rowstr[], double x[], double z[],
                      double a[], double p[], double q[], double r[],
                      double *rnorm)
{
    colidx[0] = 0;
}

static void makea(int n, int nz, double a[], int colidx[], int rowstr[],
                  int firstrow, int lastrow, int firstcol, int lastcol,
                  int arow[], int acol[][NONZER + 1], double aelt[][NONZER + 1],
                  int iv[])
{
    int iouter, ivelt, nzv, nn1;
    int ivc[NONZER + 1];
    double vc[NONZER + 1];

    //---------------------------------------------------------------------
    // nonzer is approximately  (int(sqrt(nnza /n)));
    //---------------------------------------------------------------------

    //---------------------------------------------------------------------
    // nn1 is the smallest power of two not less than n
    //---------------------------------------------------------------------
    nn1 = 1;
    do {
        nn1 = 2 * nn1;
    } while (nn1 < n);

    //---------------------------------------------------------------------
    // Generate nonzero positions and save for the use in sparse.
    //---------------------------------------------------------------------
    for (iouter = 0; iouter < n; iouter++) {
        nzv = NONZER;
        arow[iouter] = nzv;

        for (ivelt = 0; ivelt < nzv; ivelt++) {
            acol[iouter][ivelt] = ivc[ivelt] - 1;
            aelt[iouter][ivelt] = vc[ivelt];
        }
    }

    //---------------------------------------------------------------------
    // ... make the sparse matrix from list of elements with duplicates
    //     (iv is used as  workspace)
    //---------------------------------------------------------------------
}

//---------------------------------------------------------------------
// rows range from firstrow to lastrow
// the rowstr pointers are defined for nrows = lastrow-firstrow+1 values
//---------------------------------------------------------------------
static void sparse(double a[], int colidx[], int rowstr[], int n, int nz,
                   int nozer, int arow[], int acol[][NONZER + 1],
                   double aelt[][NONZER + 1], int firstrow, int lastrow,
                   int nzloc[], double rcond, double shift)
{
    int nrows;

    //---------------------------------------------------
    // generate a sparse matrix from a list of
    // [col, row, element] tri
    //---------------------------------------------------
    int i, j, j1, j2, nza, k, kk, nzrow, jcol;
    double size, scale, ratio, va;
    logical cont40;

    //---------------------------------------------------------------------
    // how many rows of result
    //---------------------------------------------------------------------
    nrows = lastrow - firstrow + 1;

    //---------------------------------------------------------------------
    // ...count the number of triples in each row
    //---------------------------------------------------------------------
    for (j = 0; j < nrows + 1; j++) {
        rowstr[j] = 0;
    }

    for (i = 0; i < n; i++) {
        for (nza = 0; nza < arow[i]; nza++) {
            j = acol[i][nza] + 1;
            rowstr[j] = rowstr[j] + arow[i];
        }
    }

    rowstr[0] = 0;
    for (j = 1; j < nrows + 1; j++) {
        rowstr[j] = rowstr[j] + rowstr[j - 1];
    }
    nza = rowstr[nrows] - 1;

    //---------------------------------------------------------------------
    // ... rowstr(j) now is the location of the first nonzero
    //     of row j of a
    //---------------------------------------------------------------------

    //---------------------------------------------------------------------
    // ... preload data pages
    //---------------------------------------------------------------------
    for (j = 0; j < nrows; j++) {
        for (k = rowstr[j]; k < rowstr[j + 1]; k++) {
            a[k] = 0.0;
            colidx[k] = -1;
        }
        nzloc[j] = 0;
    }

    //---------------------------------------------------------------------
    // ... generate actual values by summing duplicates
    //---------------------------------------------------------------------
    size = 1.0;

    for (i = 0; i < n; i++) {
        for (nza = 0; nza < arow[i]; nza++) {
            j = acol[i][nza];

            scale = size * aelt[i][nza];
            for (nzrow = 0; nzrow < arow[i]; nzrow++) {
                jcol = acol[i][nzrow];
                va = aelt[i][nzrow] * scale;

                //--------------------------------------------------------------------
                // ... add the identity * rcond to the generated matrix to bound
                //     the smallest eigenvalue from below by rcond
                //--------------------------------------------------------------------
                if (jcol == j && j == i) {
                    va = va + rcond - shift;
                }

                cont40 = false;
                for (k = rowstr[j]; k < rowstr[j + 1]; k++) {
                    if (colidx[k] > jcol) {
                        //----------------------------------------------------------------
                        // ... insert colidx here orderly
                        //----------------------------------------------------------------
                        for (kk = rowstr[j + 1] - 2; kk >= k; kk--) {
                            if (colidx[kk] > -1) {
                                a[kk + 1] = a[kk];
                                colidx[kk + 1] = colidx[kk];
                            }
                        }
                        colidx[k] = jcol;
                        a[k] = 0.0;
                        cont40 = true;
                        break;
                    }
                    else if (colidx[k] == -1) {
                        colidx[k] = jcol;
                        cont40 = true;
                        break;
                    }
                    else if (colidx[k] == jcol) {
                        //--------------------------------------------------------------
                        // ... mark the duplicated entry
                        //--------------------------------------------------------------
                        nzloc[j] = nzloc[j] + 1;
                        cont40 = true;
                        break;
                    }
                }
                a[k] = a[k] + va;
            }
        }
        size = size * ratio;
    }

    //---------------------------------------------------------------------
    // ... remove empty entries and generate final results
    //---------------------------------------------------------------------
    for (j = 1; j < nrows; j++) {
        nzloc[j] = nzloc[j] + nzloc[j - 1];
    }

    for (j = 0; j < nrows; j++) {
        if (j > 0) {
            j1 = rowstr[j] - nzloc[j - 1];
        }
        else {
            j1 = 0;
        }
        j2 = rowstr[j + 1] - nzloc[j];
        nza = rowstr[j];
        for (k = j1; k < j2; k++) {
            a[k] = a[nza];
            colidx[k] = colidx[nza];
            nza = nza + 1;
        }
    }
    for (j = 1; j < nrows + 1; j++) {
        rowstr[j] = rowstr[j] - nzloc[j - 1];
    }
    nza = rowstr[nrows] - 1;
}

//---------------------------------------------------------------------
// generate a sparse n-vector (v, iv)
// having nzv nonzeros
//
// mark(i) is set to 1 if position i is nonzero.
// mark is all zero on entry and is reset to all zero before exit
// this corrects a performance bug found by John G. Lewis, caused by
// reinitialization of mark on every one of the n calls to sprnvc
//---------------------------------------------------------------------
static void sprnvc(int n, int nz, int nn1, double v[], int iv[]) { return; }

//---------------------------------------------------------------------
// scale a double precision number x in (0,1) by a power of 2 and chop it
//---------------------------------------------------------------------
static int icnvrt(double x, int ipwr2) { return (int)(ipwr2 * x); }

//---------------------------------------------------------------------
// set ith element of sparse vector (v, iv) with
// nzv nonzeros to val
//---------------------------------------------------------------------
static void vecset(int n, double v[], int iv[], int *nzv, int i, double val)
{
    return;
}
