#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "npbparams.h"
#include "type.h"

//---------------------------------------------------------------------
// rows range from firstrow to lastrow
// the rowstr pointers are defined for nrows = lastrow-firstrow+1 values
//---------------------------------------------------------------------
void sparse(double a[], int colidx[], int rowstr[], int n, int nz, int nozer,
            int arow[], int acol[][NONZER + 1], double aelt[][NONZER + 1],
            int firstrow, int lastrow, int nzloc[], double rcond, double shift)
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
        //    exit(EXIT_FAILURE);
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
                    //          exit(EXIT_FAILURE);
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

int main() { return 0; }