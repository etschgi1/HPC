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

struct mm_input {
    size_t rows;
    size_t cols;
    double *a;  
    double *b;  
}MM_input;

char* getbuffer(mm_input *in, size_t size_of_buffer){
    char* buffer = (char*)malloc(size_of_buffer);
    if (buffer == 0)
    {
        printf("Buffer couldn't be allocated.");
        return NULL;
    }

    memcpy(buffer, &in.rows, sizeof(size_t));
    memcpy(buffer + sizeof(size_t), &in.cols, sizeof(size_t));
    memcpy(buffer + 2*sizeof(size_t), in.a, in.rows*in.cols*sizeof(double));
    memcpy(buffer + 2*sizeof(size_t) + in.rows*in.cols*sizeof(double), in.b, in.rows*in.cols*sizeof(double));
    return buffer;
}


void setupMatrices(double (*a)[NCA], double (*b)[NCB], double (*c)[NCB]){
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
}

double productSequential(double *res) {
    // dynamically allocate to not run into stack overflow - usually stacks are
    // 8192 bytes big -> 1024 doubles but we have 1 Mio. per matrix
    double(*a)[NCA] = malloc(sizeof(double) * NRA * NCA);
    double(*b)[NCB] = malloc(sizeof(double) * NCA * NCB);
    double(*c)[NCB] = malloc(sizeof(double) * NRA * NCB);

    /*** Initialize matrices ***/
    setupMatrices(a,b,c);

    /* Parallelize the computation of the following matrix-matrix
   multiplication. How to partition and distribute the initial matrices, the
   work, and collecting final results.
    */
    // multiply
    double start = MPI_Wtime();
    for (size_t i = 0; i < NRA; i++) {
        for (size_t j = 0; j < NCB; j++) {
            for (size_t k = 0; k < NCA; k++) {
                c[i][j] += a[i][k] * b[k][j];
            }
        }
    }
    double time = MPI_Wtime()-start;
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
    return time;
}

int splitwork(size_t num_workers){
    
    double(*a)[NCA] = malloc(sizeof(double) * NRA * NCA);
    double(*b)[NCB] = malloc(sizeof(double) * NCA * NCB);
    double(*c)[NCB] = malloc(sizeof(double) * NRA * NCB);
    // Transpose matrix b to make accessing columns easier - in row major way - better cache performance
    double (*b_transposed)[NCA] = malloc(sizeof(double) * NCA * NCB);
    for (size_t i = 0; i < NCA; i++) {
        for (size_t j = 0; j < NCB; j++) {
            b_transposed[j][i] = b[i][j];
        }
    }

    /*** Initialize matrices ***/
    setupMatrices(a,b,c);
    // given number of workers I'll split
    size_t rows_per_worker = NRA / (num_workers+1); //takes corresponding columns from other matrix
    printf("rows per worker: %zu\n", rows_per_worker);
    size_t row_end_first = NRA - rows_per_worker*num_workers; 
    printf("first gets most: %zu\n", row_end_first);

    //setup requests
    MPI_Request[num_workers] requests;
    MM_input data_first; 
    data_first.rows = row_end_first;
    data_first.cols = row_end_first;
    data_first.a = a; //they both start of with no offset!
    data_first.b = b;
    //first one
    // MPI_Isend();
    for (size_t i = 0; i < (num_workers-1); i++)
    {
        MM_input data;
        data.rows = rows_per_worker;
        data.cols = rows_per_worker;
        data.a = &(a[row_end_first + rows_per_worker*i]);
        data.b = &(b[row_end_first + rows_per_worker*i]);
        //MPI_Isend(); // send other stuff!
    }
    //rest belongs to me!
    //TODO multiply and add rest!
    //free all pointers!
    free(a);
    free(b);
    free(b_transposed);
    free(c);
    return 0;
}

int work(){
    return 0;
}

int main(int argc, char *argv[]) {
    int tid, nthreads;
    /* for simplicity, set NRA=NCA=NCB=N  */
    // Initialize MPI, find out MPI communicator size and process rank
    int myRank, numProcs;
    MPI_Status status;
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &numProcs);
    MPI_Comm_rank(MPI_COMM_WORLD, &myRank);

    if (argc > 1 && strcmp(argv[1], "parallel") == 0) {
        // Variables for the process rank and number of processes


        if (myRank == 0) {
            printf("Run parallel!\n");
            printf("Hello from master! - I have %d workers!\n", numProcs-1);
            // send out work
            splitwork(5);
        } else {
            printf("Worker bee %d...\n", myRank);
            work();
        }

    } else  // run sequantial
    {
        printf("Run sequantial!\n");
        double *res = malloc(sizeof(double) * NRA * NCB);
        double time = productSequential(res);
        if (checkResult(res, res, NCB, NRA)) {
            printf("Matrices do not match!!!\n");
            return 1;
        }
        printf("Matrices match! - took: %.2f s\n", time);
        free(res);
    }

    MPI_Finalize();
    return 0;
}
