
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
    int j, k, it;

    double rnorm;
    double norm_temp2;

    firstrow = 0;
    lastrow = NA - 1;
    firstcol = 0;
    lastcol = NA - 1;

    printf(" Size: %11d\n", NA);

    naa = NA;
    nzz = NZ;

    for (it = 1; it <= 1; it++) {
        conj_grad(colidx, rowstr, x, z, a, p, q, r, &rnorm);

        for (j = 0; j < lastcol - firstcol + 1; j++) {
            x[j] = norm_temp2 * z[j];
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
    int j, k;
    int cgit, cgitmax = 25;
    double d, sum, rho, rho0, alpha, beta;

    rho = 0.0;

    //---------------------------------------------------------------------
    // Initialize the CG algorithm:
    //---------------------------------------------------------------------
    for (j = 0; j < naa + 1; j++) {
        q[j] = 0.0;
        z[j] = 0.0;
        r[j] = x[j];
        p[j] = r[j];
    }

    //---------------------------------------------------------------------
    // rho = r.r
    // Now, obtain the norm of r: First, sum squares of r elements locally...
    //---------------------------------------------------------------------
    for (j = 0; j < lastcol - firstcol + 1; j++) {
        rho = rho + r[j] * r[j];
    }

    //---------------------------------------------------------------------
    //---->
    // The conj grad iteration loop
    //---->
    //---------------------------------------------------------------------
    for (cgit = 1; cgit <= cgitmax; cgit++) {
        //---------------------------------------------------------------------
        // q = A.p
        // The partition submatrix-vector multiply: use workspace w
        //---------------------------------------------------------------------
        //
        // NOTE: this version of the multiply is actually (slightly: maybe %5)
        //       faster on the sp2 on 16 nodes than is the unrolled-by-2 version
        //       below.   On the Cray t3d, the reverse is true, i.e., the
        //       unrolled-by-two version is some 10% faster.
        //       The unrolled-by-8 version below is significantly faster
        //       on the Cray t3d - overall speed of code is 1.5 times faster.

        for (j = 0; j < lastrow - firstrow + 1; j++) {
            sum = 0.0;
            for (k = rowstr[j]; k < rowstr[j + 1]; k++) {
                sum = sum + a[k] * p[colidx[k]];
            }
            q[j] = sum;
        }

        for (j = 0; j < lastrow - firstrow + 1; j++) {
            int i = rowstr[j];
            int iresidue = (rowstr[j + 1] - i) % 2;
            double sum1 = 0.0;
            double sum2 = 0.0;
            if (iresidue == 1)
                sum1 = sum1 + a[i] * p[colidx[i]];
            for (k = i + iresidue; k <= rowstr[j + 1] - 2; k += 2) {
                sum1 = sum1 + a[k] * p[colidx[k]];
                sum2 = sum2 + a[k + 1] * p[colidx[k + 1]];
            }
            q[j] = sum1 + sum2;
        }

        for (j = 0; j < lastrow - firstrow + 1; j++) {
            int i = rowstr[j];
            int iresidue = (rowstr[j + 1] - i) % 8;
            double sum = 0.0;
            for (k = i; k <= i + iresidue - 1; k++) {
                sum = sum + a[k] * p[colidx[k]];
            }
            for (k = i + iresidue; k <= rowstr[j + 1] - 8; k += 8) {
                sum =
                    sum + a[k] * p[colidx[k]] + a[k + 1] * p[colidx[k + 1]] +
                    a[k + 2] * p[colidx[k + 2]] + a[k + 3] * p[colidx[k + 3]] +
                    a[k + 4] * p[colidx[k + 4]] + a[k + 5] * p[colidx[k + 5]] +
                    a[k + 6] * p[colidx[k + 6]] + a[k + 7] * p[colidx[k + 7]];
            }
            q[j] = sum;
        }

        //---------------------------------------------------------------------
        // Obtain p.q
        //---------------------------------------------------------------------
        d = 0.0;
        for (j = 0; j < lastcol - firstcol + 1; j++) {
            d = d + p[j] * q[j];
        }

        //---------------------------------------------------------------------
        // Obtain alpha = rho / (p.q)
        //---------------------------------------------------------------------
        alpha = rho / d;

        //---------------------------------------------------------------------
        // Save a temporary of rho
        //---------------------------------------------------------------------
        rho0 = rho;

        //---------------------------------------------------------------------
        // Obtain z = z + alpha*p
        // and    r = r - alpha*q
        //---------------------------------------------------------------------
        rho = 0.0;
        for (j = 0; j < lastcol - firstcol + 1; j++) {
            z[j] = z[j] + alpha * p[j];
            r[j] = r[j] - alpha * q[j];
        }

        //---------------------------------------------------------------------
        // rho = r.r
        // Now, obtain the norm of r: First, sum squares of r elements
        // locally...
        //---------------------------------------------------------------------
        for (j = 0; j < lastcol - firstcol + 1; j++) {
            rho = rho + r[j] * r[j];
        }

        //---------------------------------------------------------------------
        // Obtain beta:
        //---------------------------------------------------------------------
        beta = rho / rho0;

        //---------------------------------------------------------------------
        // p = r + beta*p
        //---------------------------------------------------------------------
        for (j = 0; j < lastcol - firstcol + 1; j++) {
            p[j] = r[j] + beta * p[j];
        }
    } // end of do cgit=1,cgitmax

    //---------------------------------------------------------------------
    // Compute residual norm explicitly:  ||r|| = ||x - A.z||
    // First, form A.z
    // The partition submatrix-vector multiply
    //---------------------------------------------------------------------
    sum = 0.0;
    for (j = 0; j < lastrow - firstrow + 1; j++) {
        d = 0.0;
        for (k = rowstr[j]; k < rowstr[j + 1]; k++) {
            d = d + a[k] * z[colidx[k]];
        }
        r[j] = d;
    }

    //---------------------------------------------------------------------
    // At this point, r contains A.z
    //---------------------------------------------------------------------
    for (j = 0; j < lastcol - firstcol + 1; j++) {
        d = x[j] - r[j];
        sum = sum + d * d;
    }

    *rnorm = sqrt(sum);
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
        sprnvc(n, nzv, nn1, vc, ivc);
        vecset(n, vc, ivc, &nzv, iouter + 1, 0.5);
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
    sparse(a, colidx, rowstr, n, nz, NONZER, arow, acol, aelt, firstrow,
           lastrow, iv, RCOND, SHIFT);
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
    if (nza > nz) {
        printf("Space for matrix elements exceeded in sparse\n");
        printf("nza, nzmax = %d, %d\n", nza, nz);
        /*exit(EXIT_FAILURE);*/ /* TODO temporary handling for Unifico */
    }

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
    ratio = pow(rcond, (1.0 / (double)(n)));

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
                if (cont40 == false) {
                    printf("internal error in sparse: i=%d\n", i);
                    /*exit(EXIT_FAILURE);*/ /* TODO temporary handling for UnASL
                                             */
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
static void sprnvc(int n, int nz, int nn1, double v[], int iv[])
{
    int nzv, ii, i;
    double vecelt, vecloc;

    nzv = 0;

    while (nzv < nz) {
        vecelt = randlc(&tran, amult);

        //---------------------------------------------------------------------
        // generate an integer between 1 and n in a portable manner
        //---------------------------------------------------------------------
        vecloc = randlc(&tran, amult);
        i = icnvrt(vecloc, nn1) + 1;
        if (i > n)
            continue;

        //---------------------------------------------------------------------
        // was this integer generated already?
        //---------------------------------------------------------------------
        logical was_gen = false;
        for (ii = 0; ii < nzv; ii++) {
            if (iv[ii] == i) {
                was_gen = true;
                break;
            }
        }
        if (was_gen)
            continue;
        v[nzv] = vecelt;
        iv[nzv] = i;
        nzv = nzv + 1;
    }
}

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
    int k;
    logical set;

    set = false;
    for (k = 0; k < *nzv; k++) {
        if (iv[k] == i) {
            v[k] = val;
            set = true;
        }
    }
    if (set == false) {
        v[*nzv] = val;
        iv[*nzv] = i;
        *nzv = *nzv + 1;
    }
}
