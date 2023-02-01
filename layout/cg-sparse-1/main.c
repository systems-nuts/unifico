#include <stdio.h>

//---------------------------------------------------------------------
// rows range from firstrow to lastrow
// the rowstr pointers are defined for nrows = lastrow-firstrow+1 values
//---------------------------------------------------------------------
void sparse(double a[], int colidx[], int rowstr[], int n, int nz, int nozer,
            int arow[], int acol[][14], double aelt[][14], int firstrow,
            int lastrow, int nzloc[], double rcond, double shift)
{
    int nrows;

    int i = 0, j = 0, j1, j2, nza, k, kk, nzrow, jcol;
    double size, scale, ratio, va;

    size = 1.0;
    for (nza = 0; nza < arow[i]; nza++) {
        j = acol[i][nza];
        if (j > 5) {
            printf("---------");
        }
    }
}

int main() { return 0; }