//-------------------------------------------------------------------------//
//                                                                         //
//  This benchmark is a serial C version of the NPB CG code. This C        //
//  version is developed by the Center for Manycore Programming at Seoul   //
//  National University and derived from the serial Fortran versions in    //
//  "NPB3.3-SER" developed by NAS.                                         //
//                                                                         //
//  Permission to use, copy, distribute and modify this software for any   //
//  purpose with or without fee is hereby granted. This software is        //
//  provided "as is" without express or implied warranty.                  //
//                                                                         //
//  Information on NPB 3.3, including the technical report, the original   //
//  specifications, source code, results and information on how to submit  //
//  new results, is available at:                                          //
//                                                                         //
//           http://www.nas.nasa.gov/Software/NPB/                         //
//                                                                         //
//  Send comments or suggestions for this C version to cmp@aces.snu.ac.kr  //
//                                                                         //
//          Center for Manycore Programming                                //
//          School of Computer Science and Engineering                     //
//          Seoul National University                                      //
//          Seoul 151-744, Korea                                           //
//                                                                         //
//          E-mail:  cmp@aces.snu.ac.kr                                    //
//                                                                         //
//-------------------------------------------------------------------------//

//-------------------------------------------------------------------------//
// Authors: Sangmin Seo, Jungwon Kim, Jun Lee, Jeongho Nah, Gangwon Jo,    //
//          and Jaejin Lee                                                 //
//-------------------------------------------------------------------------//

//---------------------------------------------------------------------
// NPB CG serial version
//---------------------------------------------------------------------

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "globals.h"

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

static void makea(int n, int nz, double a[], int colidx[], int rowstr[],
                  int firstrow, int lastrow, int firstcol, int lastcol,
                  int arow[], int acol[][NONZER + 1], double aelt[][NONZER + 1],
                  int iv[]);

static void sparse(double a[], int colidx[], int rowstr[], int n, int nz,
                   int nozer, int arow[], int acol[][NONZER + 1],
                   double aelt[][NONZER + 1], double shift)
{
    return;
}

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
    //---------------------------------------------------------------------
    //
    //---------------------------------------------------------------------
    makea(naa, nzz, a, colidx, rowstr, firstrow, lastrow, firstcol, lastcol,
          arow, (int(*)[NONZER + 1])(void *)acol,
          (double(*)[NONZER + 1])(void *)aelt, iv);

    return 0;
}

static void makea(int n, int nz, double a[], int colidx[], int rowstr[],
                  int firstrow, int lastrow, int firstcol, int lastcol,
                  int arow[], int acol[][NONZER + 1], double aelt[][NONZER + 1],
                  int iv[])
{
    sparse(a, colidx, rowstr, n, nz, NONZER, arow, acol, aelt, SHIFT);
}
