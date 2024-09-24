#include <mpi.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    MPI_Init(&argc, &argv);
    MPI_Status status;
    int rank;
    char* data = "Hello MPI!";
    char* datarev = malloc(10*sizeof(char));

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    if (rank == 0)
    {
        MPI_Recv(datarev, 10, MPI_CHAR, 1,0,MPI_COMM_WORLD, &status);
        printf("%s at Rank %d\n", datarev, rank);
    }
    else if (rank ==1)
    {
        MPI_Send(data, 10, MPI_CHAR, 0, 0, MPI_COMM_WORLD);
    }
    printf("Hello from rank %d\n", rank);
    free(datarev);
    MPI_Finalize();
    return 0;
}