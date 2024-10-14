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

#define NRA 2000 /* number of rows in matrix A */
#define NCA 2000 /* number of columns in matrix A */
#define NCB 2000 /* number of columns in matrix B */
// #define N 1000
#define EPS 1e-9
#define SIZE_OF_B NCA*NCB*sizeof(double)

bool eps_equal(double a, double b) { return fabs(a - b) < EPS; }

void print_flattened_matrix(double *matrix, size_t rows, size_t cols, int rank) {
    printf("[%d]\n", rank);
    for (size_t i = 0; i < rows; i++) {
        for (size_t j = 0; j < cols; j++) {
            printf("%10.2f ", matrix[i * cols + j]);  // Accessing element in the 1D array
        }
        printf("\n");  // Newline after each row
    }
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

typedef struct {
    size_t rows;
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
    size_t matrix_size = in->rows * NCA * sizeof(double);
    memcpy(buffer + offset, in->a, matrix_size);
    offset += matrix_size;
    memcpy(buffer + offset, in->b, NCA*NCB*sizeof(double));
    return buffer;
}

MM_input* readbuffer(char* buffer, size_t size_of_buffer){
    MM_input *mm = (MM_input*)malloc(sizeof(MM_input));

    mm->rows = ((size_t*)buffer)[0];
    size_t offset = sizeof(size_t);
    size_t matrix_size =  mm->rows * NCA;
    mm->a = (double*)malloc(sizeof(double)*matrix_size);
    mm->b = (double*)malloc(sizeof(double)*matrix_size);
    memcpy(mm->a, &(buffer[offset]), matrix_size);
    offset += matrix_size;
    memcpy(mm->b, &(buffer[offset]), NCA*NCB*sizeof(double));
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

double multsum(double* a,double* b_transposed, size_t size){
    double acc = 0;
    for (size_t i = 0; i < size; i++)
    {
        acc += a[i]*b_transposed[i];
    }
    return acc;
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
                res[i * NCB + j] += a[i][k] * b[k][j];
            }
        }
    }
    /*  perform time measurement. Always check the correctness of the parallel
       results by printing a few values of c[i][j] and compare with the
       sequential output.
    */
    double time = MPI_Wtime()-start;
    free(a);
    free(b);
    free(c);
    return time;
}

double splitwork(double* res, double*truth, size_t num_workers){
    if (num_workers == 0) // sadly noone will help me :((
    {
        printf("Run sequential!\n");
        return productSequential(res);
    }
    
    double(*a)[NCA] = malloc(sizeof(double) * NRA * NCA);
    double(*b)[NCB] = malloc(sizeof(double) * NCA * NCB);
    double(*c)[NCB] = malloc(sizeof(double) * NRA * NCB);
    // Transpose matrix b to make accessing columns easier - in row major way - better cache performance
    setupMatrices(a,b,c);

    double start_time = MPI_Wtime();
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
    data_first->a = (double*)a; //they both start of with no offset!
    data_first->b = (double*)b_transposed;
    size_t total_size = sizeof(size_t) + (data_first->rows * NCA)*sizeof(double)+SIZE_OF_B;
    char* buffer = getbuffer(data_first, total_size);    //first one

    // Tag is just nr-cpu -1
    MPI_Isend(buffer, total_size, MPI_CHAR, 1, 0,MPI_COMM_WORLD, &requests[0]);
    free(data_first);
    total_size = sizeof(size_t) + (rows_per_worker * NCA)*sizeof(double) + SIZE_OF_B; //size is the same for all other - just compute once!
    size_t i;
    for (i = 0; i < (num_workers-1); ++i)
    {
        MM_input *data = (MM_input*)malloc(sizeof(MM_input));
        data->rows = rows_per_worker;
        data->a = (double*)(a + (row_end_first + rows_per_worker*i));
        data->b = (double*)(b_transposed); // send everyting - all needed
        buffer = getbuffer(data, total_size);
        printf("nr_worker - %zu\n", i);
        MPI_Isend(buffer, total_size, MPI_CHAR, i+2, i+1,MPI_COMM_WORLD, &requests[i+1]);
        free(data);
    }
    double* my_a = (double*)(a + (row_end_first + rows_per_worker*i));

    //I multiply the rest
    size_t offset = 0;
    for (size_t row = (NRA-rows_per_worker); row < NRA; row++)
    {
        for (size_t col = 0; col < NCB; col++)
        {
            res[row * NCB + col] = multsum(my_a+offset, (((double*)b_transposed)+col*NCA), NCA);
        }
        offset += NCA;
    }
    printf("My c: \n");
    //wait for rest
    MPI_Status stats[num_workers];
    if(MPI_Waitall(num_workers, requests, stats) == MPI_ERR_IN_STATUS){
        printf("Communication failed!!! - abort\n");
    }
    printf(">>>Everything sent and recieved\n");

    // reviece rest
    size_t buf_size = sizeof(double)*row_end_first*NCB;
    double* revbuf;
    offset = 0;
    for (size_t worker = 0; worker < num_workers; worker++)
    {
        revbuf = (double*)malloc(buf_size); //first gets largest buffer
        MPI_Recv(revbuf, buf_size/sizeof(double), MPI_DOUBLE, worker+1, worker, MPI_COMM_WORLD,&stats[worker]);
        memcpy(&res[offset/sizeof(double)], revbuf, buf_size);
        free(revbuf);
        offset += buf_size;
        buf_size = sizeof(double)*rows_per_worker*NCB; 
    }
    double time = MPI_Wtime()-start_time;
    //free all pointers!
    free(a);
    free(b);
    free(b_transposed);
    free(c);
    return time;
}



double work(int rank, size_t num_workers){
    size_t rows_per_worker = NRA / (num_workers+1);
    char* buffer;
    MPI_Status status;
    if (rank == 1) // first always get's most work
    {
        rows_per_worker = NRA - rows_per_worker*num_workers; 
    }
    size_t size_of_meta = sizeof(size_t);
    size_t size_of_a = sizeof(double)*rows_per_worker*NCA;
    size_t buffersize = size_of_meta+size_of_a + SIZE_OF_B;
    buffer = (char*)malloc(buffersize);
    
    MPI_Recv(buffer, buffersize, MPI_CHAR, 0, rank-1, MPI_COMM_WORLD, &status);
    double start = MPI_Wtime();
    int count;
    MPI_Get_count(&status, MPI_CHAR, &count);
    printf("I'm rank %d and I got %d bytes (%ld doubles) of data from %d with tag %d.\n", rank, count, (count-sizeof(size_t))/sizeof(double), status.MPI_SOURCE, status.MPI_TAG);
    
    MM_input *mm = (MM_input*)malloc(sizeof(MM_input));
    mm->a = (double*)&buffer[size_of_meta];
    mm->b = (double*)&buffer[size_of_meta+size_of_a];

    double *res =(double*)malloc(sizeof(double)*rows_per_worker*NCB);

    size_t offset = 0;
    for (size_t row = 0; row < rows_per_worker; row++)
    {
        for (size_t col = 0; col < NCB; col++)
        {
            res[row * NCB + col] = multsum(mm->a+offset, (((double*)mm->b)+col*NCA), NCA);
        }
        offset += NCA;
    }
    MPI_Send(res, rows_per_worker*NCB, MPI_DOUBLE, 0,rank-1, MPI_COMM_WORLD);
    printf("[%d] sent res home\n",rank);
    free(res);
    return MPI_Wtime() - start;
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
    int num_Workers = numProcs-1;
    if (argc > 1 && strcmp(argv[1], "parallel") == 0) {
        // Variables for the process rank and number of processes
       if (myRank == 0) {
            printf("Run parallel!\n");
            double *truth = malloc(sizeof(double) * NRA * NCB);
            double time = productSequential(truth);
            printf("Computed reference results in %.6f s\n", time);
            printf("Hello from master! - I have %d workers!\n", num_Workers);
            // send out work
            double *res = malloc(sizeof(double)*NRA*NCB);
            time = splitwork(res, truth, num_Workers);
            if (checkResult(res, res, NCB, NRA)) {
                printf("Matrices do not match!!!\n");
                return 1;
            }
            printf("Matrices match (parallel [eps %.10f])! - took: %.6f s\n", EPS, time);
            free(truth);
            free(res);
        } else {
            double time = work(myRank, num_Workers);
            printf("Worker bee %d took %.6f s (after recv) for my work\n", myRank, time);
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
        printf("Matrices match (sequantial-trivial)! - took: %.6f s\n", time);
        free(res);
    }

    MPI_Finalize();
    return 0;
}
