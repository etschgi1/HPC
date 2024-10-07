/******************************************************************************
 * FILE: mm.c
 * DESCRIPTION:
 *   This program calculates the product of matrix a[nra][nca] and b[nca][ncb],
 *   the result is stored in matrix c[nra][ncb].
 *   The max dimension of the matrix is constraint with static array
 *declaration, for a larger matrix you may consider dynamic allocation of the
 *arrays, but it makes a parallel code much more complicated (think of
 *communication), so this is only optional.
 *
 ******************************************************************************/

#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#define NRA 1000 /* number of rows in matrix A */
#define NCA 1000 /* number of columns in matrix A */
#define NCB 1000 /* number of columns in matrix B */
#define N 1000
#define EPS 1e-9

bool eps_equal(double a, double b) {
    return fabs(a - b) < EPS;
}

int checkResult(double *truth, double *test, size_t Nr_col, size_t Nr_rows) {
    for (size_t i = 0; i < Nr_rows; ++i) {
        for (size_t j = 0; j < Nr_col; ++j) {
            size_t index = i * Nr_col + j;
            if (!eps_equal(truth[index], test[index])) {
                return 1;
            }
        }
    }
    return 0;
}

int productSequential(double *res) {
    double a[NRA][NCA], /* matrix A to be multiplied */
        b[NCA][NCB],    /* matrix B to be multiplied */
        c[NRA][NCB];    /* result matrix C */

    /*** Initialize matrices ***/

    for (size_t i = 0; i < NRA; i++) {
        for (size_t j = 0; j < NCA; j++) {
            a[i][j] = i + j;
        }
    }

    for (size_t i = 0; i < NCA; i++) {
        for (size_t j = 0; j < NCB; j++) {
            b[i][j] = i * j;
        }
    }

    for (size_t i = 0; i < NRA; i++) {
        for (size_t j = 0; j < NCB; j++) {
            c[i][j] = 0;
        }
    }
    // multiply
    for (size_t i = 0; i < NRA; i++) {
        for (size_t j = 0; j < NCB; j++) {
            for (size_t k = 0; k < NCA; k++) {
                c[i][j] += a[i][k] * b[k][j];
            }
        }
    }

    /* Parallelize the computation of the following matrix-matrix multiplication.
   How to partition and distribute the initial matrices, the work, and
   collecting final results.
*/

    // write to res
    for (size_t i = 0; i < NRA; i++) {
        for (size_t j = 0; j < NCB; j++) {
            res[i * NCB + j] = c[i][j];
        }
    }

    /*  perform time measurement. Always check the correctness of the parallel
       results by printing a few values of c[i][j] and compare with the sequential
       output.
    */
    return 0;
}

int main(int argc, char *argv[]) {
    int tid, nthreads, i, j, k;
    /* for simplicity, set NRA=NCA=NCB=N  */

    double *res = malloc(sizeof(double) * NRA * NCB);
    productSequential(res);

    return 0;
}
