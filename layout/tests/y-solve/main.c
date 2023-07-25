#include "header.h"

#define BLOCK_SIZE 5

int grid_points[3];
double rhs2[10][10 + 1][10 + 1][5];
double lhs[1][3][5][5];

void y_solve()
{
    int i, j, k, m, n, jsize;

    jsize = grid_points[1];

    for (k = 1; k <= grid_points[2] - 2; k++) {
        for (i = 1; i <= grid_points[0] - 2; i++) {
            lhsinit(lhs, jsize);
            for (j = jsize - 1; j >= 0; j--) {
                for (m = 0; m < BLOCK_SIZE; m++) {
                    for (n = 0; n < BLOCK_SIZE; n++) {
                        rhs2[k][j][i][m] =
                            lhs[0][0][n][m] * rhs2[k][j + 1][i][n];
                    }
                }
            }
        }
    }
}

int main(int argc, char *argv[])
{
    y_solve();

    return 0;
}
