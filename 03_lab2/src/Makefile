# Add -g for debug symbols
CC = mpicc

FP_CFLAGS = -g
FP_LIBS = -lm
GD_LIBS = -lm

FP_OBJS = MPI_Fempois.o
GD_OBJS = GridDist.o

all: clean MPI_Fempois.out GridDist.out

run: all
	./GridDist.out 2 2 100 100
	mpirun -np 4 ./MPI_Fempois.out

sequential: 
	gcc -g -o SEQ_Poisson.out SEQ_Poisson.c 
	./SEQ_Poisson.out

clean:
	rm -f *.o 
	rm -f *.out
	rm -f input[0-9]-[0-9].dat
	rm -f output[0-9]-[0-9].dat
	rm -f mapping*.dat

MPI_Fempois.out: $(FP_OBJS)
	mpicc $(FP_CFLAGS) -o $@ $(FP_OBJS) $(FP_LIBS)

GridDist.out: $(GD_OBJS)
	gcc -g -o $@ $(GD_OBJS) $(GD_LIBS)

MPI_Fempois.o:
	mpicc $(FP_CFLAGS) -c MPI_Fempois.c

GridDist.o:
	gcc -g -c GridDist.c
