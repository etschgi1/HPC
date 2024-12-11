# Add -g for debug symbols
CC = mpicc
CFLAGS = -g
FP_LIBS = -lm
GD_LIBS = -lm

FP_OBJS = MPI_Fempois.o
GD_OBJS = GridDist.o

all: clean MPI_Fempois.out GridDist.out

run: all
	./GridDist.out 2 2 100 100 adapt
	mpirun -np 4 ./MPI_Fempois.out

# Score-P targets
MPI_Fempois_score.out: $(FP_OBJS)
	scorep $(CC) $(CFLAGS) -o $@ $(FP_OBJS) $(FP_LIBS)

GridDist_score.out: $(GD_OBJS)
	gcc $(CFLAGS) -o $@ $(GD_OBJS) $(GD_LIBS)

allscore: clean GridDist_score.out MPI_Fempois_score.out

runscore: allscore
	./GridDist_score.out 2 2 100 100
	SCOREP_ENABLE_TRACING=true scorep mpirun -np 4 ./MPI_Fempois_score.out

sequential: 
	gcc $(CFLAGS) -o SEQ_Poisson.out SEQ_Poisson.c 
	./SEQ_Poisson.out

clean:
	rm -f *.o 
	rm -f *.out
	rm -f input[0-9]-[0-9].dat
	rm -f output[0-9]-[0-9].dat
	rm -f mapping*.dat
	rm -rf scorep-*

MPI_Fempois.out: $(FP_OBJS)
	$(CC) $(CFLAGS) -o $@ $(FP_OBJS) $(FP_LIBS)

GridDist.out: $(GD_OBJS)
	gcc $(CFLAGS) -o $@ $(GD_OBJS) $(GD_LIBS)

MPI_Fempois.o:
	$(CC) $(CFLAGS) -c MPI_Fempois.c

GridDist.o:
	gcc $(CFLAGS) -c GridDist.c
