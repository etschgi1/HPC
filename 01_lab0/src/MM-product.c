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

typedef struct {
    size_t rows;
    size_t cols;
    double *a;  
    double *b;  
} MM_input;

char* getbuffer(MM_input *in, size_t size_of_buffer){
    char* buffer = (char*)malloc(size_of_buffer * sizeof(char));
    if (buffer == 0)
    {
        printf("Buffer couldn't be allocated.");
        return NULL;
    }
    size_t offset = 0;
    memcpy(buffer + offset, &in->rows, sizeof(size_t));
    offset += sizeof(size_t);
    memcpy(buffer + offset, &in->cols, sizeof(size_t));
    offset += sizeof(size_t);
    size_t matrix_size = in->rows * in->cols * sizeof(double);
    memcpy(buffer + offset, in->a, matrix_size);
    offset += matrix_size;
    memcpy(buffer + offset, in->b, matrix_size);
    return buffer;
}

MM_input* readbuffer(char* buffer, size_t size_of_buffer){
    MM_input *mm = (MM_input*)malloc(sizeof(MM_input));

    mm->rows = ((size_t*)buffer)[0];
    mm->cols = ((size_t*)buffer)[1];
    size_t offset = 2*sizeof(size_t);
    size_t matrix_size =  mm->rows * mm->cols;
    mm->a = (double*)malloc(sizeof(double)*matrix_size);
    mm->b = (double*)malloc(sizeof(double)*matrix_size);
    memcpy(a, &(buffer[offset]), matrix_size);
    offset += matrix_size;
    memcpy(b, &(buffer[offset]), matrix_size);
    free(buffer);
    return mm;
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

double splitwork(double* res, size_t num_workers){
    // if (num_workers == 0) // sadly noone will help me :((
    // {
    //     printf("Run sequential!");
    //     return productSequential(res);
    // }
    
    double(*a)[NCA] = malloc(sizeof(double) * NRA * NCA);
    double(*b)[NCB] = malloc(sizeof(double) * NCA * NCB);
    double(*c)[NCB] = malloc(sizeof(double) * NRA * NCB);
    // Transpose matrix b to make accessing columns easier - in row major way - better cache performance
    setupMatrices(a,b,c);

    double (*b_transposed)[NCA] = malloc(sizeof(double) * NCA * NCB);
    for (size_t i = 0; i < NCA; i++) {
        for (size_t j = 0; j < NCB; j++) {
            b_transposed[j][i] = b[i][j];
        }
    }

    /*** Initialize matrices ***/
    // given number of workers I'll split
    size_t rows_per_worker = NRA / (num_workers+1); //takes corresponding columns from other matrix
    printf("rows per worker: %zu\n", rows_per_worker);
    size_t row_end_first = NRA - rows_per_worker*num_workers; 
    printf("first gets most: %zu\n", row_end_first);

    //setup requests
    MPI_Request requests[num_workers];
    MM_input *data_first = (MM_input*)malloc(sizeof(MM_input));
    data_first->rows = row_end_first;
    data_first->cols = row_end_first;
    data_first->a = (double*)a; //they both start of with no offset!
    data_first->b = (double*)b_transposed;
    size_t total_size = 2*sizeof(size_t) + 2*(data_first->rows * data_first->cols)*sizeof(double);
    char* buffer = getbuffer(data_first, total_size);    //first one
    // Tag is just nr-cpu -1
    MPI_Isend(buffer, total_size, MPI_CHAR, 1, 0,MPI_COMM_WORLD, requests[0]);
    total_size = 2*sizeof(size_t) + 2*(rows_per_worker * rows_per_worker)*sizeof(double); //size is the same for all other - just compute once!
    size_t i;
    for (i = 0; i < (num_workers-1); ++i)
    {
        MM_input *data = (MM_input*)malloc(sizeof(MM_input));
        data->rows = rows_per_worker;
        data->cols = rows_per_worker;
        data->a = (double*)(a + (row_end_first + rows_per_worker*i));
        data->b = (double*)(b_transposed+(row_end_first + rows_per_worker*i));
        buffer = getbuffer(data, total_size);
        printf("nr_worker - %zu\n", i);
        MPI_Isend(buffer, total_size, MPI_CHAR, i+2, i+1,MPI_COMM_WORLD, requests[i+1]);
    }
    printf("me %zu\n", i);
    //rest belongs to me!

    //TODO multiply and add rest!
    //free all pointers!
    free(a);
    free(b);
    free(b_transposed);
    free(c);
    return 0;
}

int work(int rank, size_t num_workers){
    size_t rows_per_worker = NRA / (num_workers+1);
    char* buffer;
    if (rank == 1) // first always get's most work
    {
        size_t row_end_first = NRA - rows_per_worker*num_workers; 
        buffer = (char*)malloc(sizeof(char)*row_end_first*row_end_first)
    }
    
    MPI_recv()
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
            double *res = malloc(sizeof(double)*NRA*NCB);
            double time = splitwork(res, numProcs-1);
            free(res);
        } else {
            printf("Worker bee %d...\n", myRank);
            work(myRank);
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
