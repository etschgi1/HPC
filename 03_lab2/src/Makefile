CC = mpicc

FP_LIBS = -lm
GD_LIBS = -lm

FP_OBJS = MPI_Fempois.o
GD_OBJS = GridDist.o

all: clean MPI_Fempois.out GridDist.out

clean:
	rm -f *.o 
	rm -f *.out
	rm -f input*.dat
	rm -f mapping*.dat

MPI_Fempois.out: $(FP_OBJS)
	mpicc -o $@ $(FP_OBJS) $(FP_LIBS)

GridDist.out: $(GD_OBJS)
	gcc -o $@ $(GD_OBJS) $(GD_LIBS)

MPI_Fempois.o:
	mpicc -c MPI_Fempois.c

GridDist.o:
	gcc -c GridDist.c