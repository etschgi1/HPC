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
#include <mpi.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NRA 1000 /* number of rows in matrix A */
#define NCA 1000 /* number of columns in matrix A */
#define NCB 1000 /* number of columns in matrix B */
// #define N 1000
#define EPS 1e-9

bool eps_equal(double a, double b) { return fabs(a - b) < EPS; }

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
    // dynamically allocate to not run into stack overflow - usually stacks are
    // 8192 bytes big -> 1024 doubles but we have 1 Mio. per matrix
    double(*a)[NCA] = malloc(sizeof(double) * NRA * NCA);
    double(*b)[NCB] = malloc(sizeof(double) * NCA * NCB);
    double(*c)[NCB] = malloc(sizeof(double) * NRA * NCB);

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
    /* Parallelize the computation of the following matrix-matrix
   multiplication. How to partition and distribute the initial matrices, the
   work, and collecting final results.
*/
    // multiply
    for (size_t i = 0; i < NRA; i++) {
        for (size_t j = 0; j < NCB; j++) {
            for (size_t k = 0; k < NCA; k++) {
                c[i][j] += a[i][k] * b[k][j];
            }
        }
    }

    /*  perform time measurement. Always check the correctness of the parallel
       results by printing a few values of c[i][j] and compare with the
       sequential output.
    */

    // write to res - no time measured here!
    for (size_t i = 0; i < NRA; i++) {
        for (size_t j = 0; j < NCB; j++) {
            res[i * NCB + j] = c[i][j];
        }
    }
    free(a);
    free(b);
    free(c);
    return 0;
}

int main(int argc, char *argv[]) {
    int tid, nthreads, i, j, k;
    /* for simplicity, set NRA=NCA=NCB=N  */

    if (argc > 1 && strcmp(argv[1], "parallel") == 0) {
        // Variables for the process rank and number of processes
        int myRank, numProcs, i;
        MPI_Status status;

        // Initialize MPI, find out MPI communicator size and process rank
        MPI_Init(&argc, &argv);
        MPI_Comm_size(MPI_COMM_WORLD, &numProcs);
        MPI_Comm_rank(MPI_COMM_WORLD, &myRank);

        if (myRank == 0) {
            printf("Run parallel!\n");
            printf("Hello from master!\n");
        } else {
            printf("Worker bee %d...\n", myRank);
        }

        MPI_Finalize();
    } else  // run sequantial
    {
        printf("Run sequantial!\n");
        double *res = malloc(sizeof(double) * NRA * NCB);
        productSequential(res);
        if (checkResult(res, res, NCB, NRA)) {
            printf("Matrices do not match!!!\n");
            return 1;
        }
        printf("Matrices match!\n");
        free(res);
    }

    return 0;
}
