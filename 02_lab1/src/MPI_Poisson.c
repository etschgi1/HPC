/*
 * MPI_Poisson.c
 * 2D Poison equation solver (parallel version)
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <mpi.h>
#include <assert.h>

#define DEBUG 0

#define max(a,b) ((a)>(b)?a:b)


// defines for Exercises!

#define SOR 1
#define MONITOR_ERROR 1
#define FAST_DO_STEP_LOOP
// #define MONITOR_ALLREDUCE 1
// #define ALLREDUCE_COUNT 100
#define MONITOR_EXCHANGE_BORDERS
#define SKIP_EXCHANGE

#define DEFINES_ON (SOR || MONITOR_ERROR || 0)
//defines end

enum
{
    X_DIR, Y_DIR
};

// only needed for certain configs!
#ifdef SOR
double sor_omega = 1.9;
#endif
#ifdef MONITOR_ERROR
double *errors=NULL;
#endif
#ifdef MONITOR_ALLREDUCE
double all_reduce_time = 0;
#endif
#ifdef MONITOR_EXCHANGE_BORDERS
double total_exchange_time = 0.0;   // Total time spent in exchanges
double total_latency = 0.0;         // Total latency
double total_data_transferred = 0.0; // Total data transferred
int num_exchanges = 0;              // Number of exchanges
#endif
#ifdef SKIP_EXCHANGE
size_t skip_exchange;
#endif

/* global variables */
int gridsize[2];
double precision_goal;		/* precision_goal of solution */
int max_iter;			/* maximum number of iterations alowed */
int P; //total number of processes
int P_grid[2]; // process grid dimensions
MPI_Comm grid_comm; //grid communicator
MPI_Status status; 
double hx, hy;

/* process specific globals*/
int proc_rank;
double wtime;
int proc_coord[2]; // coords of current process in processgrid
int proc_top, proc_right, proc_bottom, proc_left; // ranks of neighboring procs
// step 7
int offset[2] = {0,0};
// step 8
MPI_Datatype border_type[2];

/* benchmark related variables */
clock_t ticks;			/* number of systemticks */
int timer_on = 0;		/* is timer running? */

/* local grid related variables */
double **phi;			/* grid */
int **source;			/* TRUE if subgrid element is a source */
int dim[2];			/* grid dimensions */

void Setup_Grid();
double Do_Step(int parity);
void Solve();
void Write_Grid();
void Clean_Up();
void Debug(char *mesg, int terminate);
void start_timer();
void resume_timer();
void stop_timer();
void print_timer();

void start_timer()
{
    if (!timer_on){
        MPI_Barrier(grid_comm);
        ticks = clock();
        wtime = MPI_Wtime(); 
        timer_on = 1;
    }
}

void resume_timer()
{
    if (!timer_on){
        ticks = clock()  -  ticks; 
        wtime = MPI_Wtime() - wtime; 
        timer_on = 1;
    }
}

void stop_timer()
{
    if (timer_on){
        ticks = clock()  -  ticks; 
        wtime = MPI_Wtime() - wtime; 
        timer_on = 0;
    }
}

void print_timer()
{
    if (timer_on){
        stop_timer();
        printf("(%i) Elapsed Wtime %14.6f s (%5.1f%% CPU)\n", proc_rank, wtime, 100.0 * ticks * (1.0 / CLOCKS_PER_SEC) / wtime); 
        resume_timer();
    }
    else{
        printf("(%i) Elapsed Wtime %14.6f s (%5.1f%% CPU)\n", proc_rank, wtime, 100.0 * ticks * (1.0 / CLOCKS_PER_SEC) / wtime);
    }
}

void Debug(char *mesg, int terminate)
{
    if (DEBUG || terminate){
        printf("%s\n", mesg);
    }
    if (terminate){
        exit(1);
    }
}

void Setup_Proc_Grid(int argc, char **argv){
    int wrap_around[2];
    int reorder;

    Debug("My_MPI_Init",0);

    // num of processes
    MPI_Comm_size(MPI_COMM_WORLD, &P);

    //calculate the number of processes per column and per row for the grid
    if(argc>2){
        P_grid[X_DIR] = atoi(argv[1]);
        P_grid[Y_DIR] = atoi(argv[2]);
        if(P_grid[X_DIR] * P_grid[Y_DIR] != P){
            Debug("ERROR Proces grid dimensions do not match with P ", 1); 
        }
        #ifdef SOR
        if (argc>3)
        {
            // get sor from args
            sor_omega = atof(argv[3]);
            printf("Set sor_omega over argv to %1.4f\n", sor_omega);
        }
        #endif
        #ifdef SKIP_EXCHANGE
        if (argc > 4)
        {
            skip_exchange = atoi(argv[4]);
            printf("Set skip_exchange over argv to %zu\n", skip_exchange);
        }
        else{
            skip_exchange = 1;
            printf("Set skip_exchange to default value 1\n");
        }
        #endif
    }    
    else{
        Debug("ERROR Wrong parameter input",1);
    }

    // Create process topology (2D grid)
    wrap_around[X_DIR] = 0;
    wrap_around[Y_DIR] = 0;
    reorder = 1; //reorder process ranks

    // create grid_comm
    int ret = MPI_Cart_create(MPI_COMM_WORLD, 2, P_grid, wrap_around, reorder, &grid_comm);
    if (ret != MPI_SUCCESS){
        Debug("ERROR: MPI_Cart_create failed",1);
    }
    //get new rank and cartesian coords of this proc
    MPI_Comm_rank(grid_comm, &proc_rank);
    MPI_Cart_coords(grid_comm, proc_rank, 2, proc_coord);
    printf("(%i) (x,y)=(%i,%i)\n", proc_rank, proc_coord[X_DIR], proc_coord[Y_DIR]); 
    //calc neighbours
    // MPI_Cart_shift(grid_comm, Y_DIR, 1, &proc_bottom, &proc_top);
    MPI_Cart_shift(grid_comm, Y_DIR, 1, &proc_top, &proc_bottom);
    MPI_Cart_shift(grid_comm, X_DIR, 1, &proc_left, &proc_right);
    printf("(%i) top %i,  right  %i,  bottom  %i,  left  %i\n", proc_rank, proc_top, proc_right, proc_bottom, proc_left);
}

void Setup_Grid()
{
    int x, y, s;
    double source_x, source_y, source_val;
    FILE *f;

    Debug("Setup_Subgrid", 0);

    if(proc_rank == 0){
        f = fopen("input.dat", "r");
        if (f == NULL){
            Debug("Error opening input.dat", 1);
        }
        fscanf(f, "nx: %i\n", &gridsize[X_DIR]);
        fscanf(f, "ny: %i\n", &gridsize[Y_DIR]);
        fscanf(f, "precision goal: %lf\n", &precision_goal);
        fscanf(f, "max iterations: %i\n", &max_iter);
    }
    MPI_Bcast(&gridsize, 2, MPI_INT, 0, grid_comm);
    MPI_Bcast(&precision_goal, 1, MPI_DOUBLE, 0, grid_comm);
    MPI_Bcast(&max_iter, 1, MPI_INT, 0, grid_comm);
    hx = 1 / (double)gridsize[X_DIR];
    hy = 1 / (double)gridsize[Y_DIR];

    /* Calculate dimensions of local subgrid */ //! We do that later now!
    // dim[X_DIR] = gridsize[X_DIR] + 2;
    // dim[Y_DIR] = gridsize[Y_DIR] + 2;

    //! Step 7
    int upper_offset[2] = {0,0};
    // Calculate top left corner cordinates of local grid
    offset[X_DIR] = gridsize[X_DIR] * proc_coord[X_DIR] / P_grid[X_DIR];
    offset[Y_DIR] = gridsize[Y_DIR] * proc_coord[Y_DIR] / P_grid[Y_DIR];
    upper_offset[X_DIR] = gridsize[X_DIR] * (proc_coord[X_DIR] + 1) / P_grid[X_DIR];
    upper_offset[Y_DIR] = gridsize[Y_DIR] * (proc_coord[Y_DIR] + 1) / P_grid[Y_DIR];

    // dimensions of local grid
    dim[X_DIR] = upper_offset[X_DIR] - offset[X_DIR];
    dim[Y_DIR] = upper_offset[Y_DIR] - offset[Y_DIR];
    // Add space for rows/columns of neighboring grid
    dim[X_DIR] += 2;
    dim[Y_DIR] += 2;
    //! Step 7 end

    /* allocate memory */
    if ((phi = malloc(dim[X_DIR] * sizeof(*phi))) == NULL){
        Debug("Setup_Subgrid : malloc(phi) failed", 1);
    }
    if ((source = malloc(dim[X_DIR] * sizeof(*source))) == NULL){
        Debug("Setup_Subgrid : malloc(source) failed", 1);
    }
    if ((phi[0] = malloc(dim[Y_DIR] * dim[X_DIR] * sizeof(**phi))) == NULL){
        Debug("Setup_Subgrid : malloc(*phi) failed", 1);
    }
    if ((source[0] = malloc(dim[Y_DIR] * dim[X_DIR] * sizeof(**source))) == NULL){
        Debug("Setup_Subgrid : malloc(*source) failed", 1);
    }
    for (x = 1; x < dim[X_DIR]; x++)
    {
        phi[x] = phi[0] + x * dim[Y_DIR];
        source[x] = source[0] + x * dim[Y_DIR];
    }

    /* set all values to '0' */
    for (x = 0; x < dim[X_DIR]; x++){
        for (y = 0; y < dim[Y_DIR]; y++)
        {
            phi[x][y] = 0.0;
            source[x][y] = 0;
        }
    }
    /* put sources in field */
    do{
        if (proc_rank==0)
        {
            s = fscanf(f, "source: %lf %lf %lf\n", &source_x, &source_y, &source_val);
        }
        MPI_Bcast(&s, 1, MPI_INT, 0, grid_comm);
        if (s==3){
            MPI_Bcast(&source_x, 1, MPI_DOUBLE, 0, grid_comm);
            MPI_Bcast(&source_y, 1, MPI_DOUBLE, 0, grid_comm);
            MPI_Bcast(&source_val, 1, MPI_DOUBLE, 0, grid_comm);
            x = source_x * gridsize[X_DIR];
            y = source_y * gridsize[Y_DIR];
            x = x + 1 - offset[X_DIR]; // Step 7 --> local grid transform
            y = y + 1 - offset[Y_DIR]; // Step 7 --> local grid transform
            if(x > 0 && x < dim[X_DIR] -1 && y > 0 && y < dim[Y_DIR]-1){ // check if in local grid
                phi[x][y] = source_val;
                source[x][y] = 1;
            }
        }
    }
    while (s==3);
    
    if(proc_rank==0){
        fclose(f);
    }
}

void Setup_MPI_Datatypes()
{
    Debug("Setup_MPI_Datatypes",0);
    
    // vertical data exchange (Y_Dir)
    MPI_Type_vector(dim[X_DIR] - 2, 1, dim[Y_DIR], MPI_DOUBLE, &border_type[Y_DIR]);
    // horizontal data exchange (X_Dir)
    MPI_Type_vector(dim[Y_DIR] - 2, 1, 1, MPI_DOUBLE, &border_type[X_DIR]);

    MPI_Type_commit(&border_type[Y_DIR]);
    MPI_Type_commit(&border_type[X_DIR]);
}

int Exchange_Borders()
{
    #ifdef MONITOR_EXCHANGE_BORDERS
    double start_time, latency_start, latency;
    double data_size_top, data_size_left;
    double exchange_time;

    // Measure latency with a small dummy message
    latency_start = MPI_Wtime();
    double dummy;
    MPI_Sendrecv(&dummy, 1, MPI_DOUBLE, proc_top, 0, &dummy, 1, MPI_DOUBLE, proc_bottom, 0, grid_comm, &status);
    latency = MPI_Wtime() - latency_start;
    total_latency += latency;

    // Calculate data sizes
    data_size_top = dim[X_DIR] * sizeof(double);  // Top and bottom rows
    data_size_left = dim[Y_DIR] * sizeof(double); // Left and right columns
    double data_transferred = 2 * (data_size_top + data_size_left); // Total data for this exchange
    total_data_transferred += data_transferred;
    #endif

    Debug("Exchange_Borders",0);
    #ifdef MONITOR_EXCHANGE_BORDERS
    start_time = MPI_Wtime();
    #endif
    // top direction
    MPI_Sendrecv(&phi[1][1], 1, border_type[Y_DIR], proc_top, 0, &phi[1][dim[Y_DIR] - 1], 1, border_type[Y_DIR], proc_bottom, 0, grid_comm, &status);
    // bottom direction
    MPI_Sendrecv(&phi[1][dim[Y_DIR] - 2], 1, border_type[Y_DIR], proc_bottom, 0, &phi[1][0], 1, border_type[Y_DIR], proc_top, 0, grid_comm, &status);
    // left direction
    MPI_Sendrecv(&phi[1][1], 1, border_type[X_DIR], proc_left, 0, &phi[dim[X_DIR]-1][1], 1, border_type[X_DIR], proc_right, 0, grid_comm, &status);
    // right direction
    MPI_Sendrecv(&phi[dim[X_DIR]-2][1], 1, border_type[X_DIR], proc_right, 0, &phi[0][1], 1, border_type[X_DIR], proc_left, 0, grid_comm, &status);

    #ifdef MONITOR_EXCHANGE_BORDERS
    exchange_time = MPI_Wtime() - start_time;
    total_exchange_time += exchange_time;
    num_exchanges++;
    #endif
    return 1;
}

double Do_Step(int parity)
{
    int x, y;
    double old_phi, c_ij;
    double max_err = 0.0;
  
    #ifdef FAST_DO_STEP_LOOP
    int start_y;
    for (x = 1; x < dim[X_DIR] - 1; x++){
        start_y = ((1 + x + offset[X_DIR] + offset[Y_DIR]) % 2 == parity) ? 1 : 2;
        for (y = start_y; y < dim[Y_DIR] - 1; y += 2){
            if (source[x][y] != 1){
                old_phi = phi[x][y];
                #ifndef SOR
                phi[x][y] = (phi[x + 1][y] + phi[x - 1][y] + phi[x][y + 1] + phi[x][y - 1]) * 0.25;
                #endif
                #ifdef SOR 
                c_ij = (phi[x + 1][y] + phi[x - 1][y] + phi[x][y + 1] + phi[x][y - 1] + hx*hy*source[x][y]) * 0.25 - phi[x][y];
                phi[x][y] += sor_omega*c_ij;
                #endif 
                if (max_err < fabs(old_phi - phi[x][y])){
                    max_err = fabs(old_phi - phi[x][y]);
                }
            }
        }
    }
    return max_err;
    #endif

    #ifndef FAST_DO_STEP_LOOP
    /* calculate interior of grid */
    for (x = 1; x < dim[X_DIR] - 1; x++){
        for (y = 1; y < dim[Y_DIR] - 1; y++){
            if ((x + offset[X_DIR] + y + offset[Y_DIR]) % 2 == parity && source[x][y] != 1){
                old_phi = phi[x][y];
                #ifndef SOR
                phi[x][y] = (phi[x + 1][y] + phi[x - 1][y] + phi[x][y + 1] + phi[x][y - 1]) * 0.25;
                #endif
                #ifdef SOR 
                c_ij = (phi[x + 1][y] + phi[x - 1][y] + phi[x][y + 1] + phi[x][y - 1] + hx*hy*source[x][y]) * 0.25 - phi[x][y];
                phi[x][y] += sor_omega*c_ij;
                #endif 
                if (max_err < fabs(old_phi - phi[x][y])){
                    max_err = fabs(old_phi - phi[x][y]);
                }
            }
        }
    }
  return max_err;
  #endif
}

void Solve()
{
    int count = 0;
    double delta;
    double global_delta;
    double delta1, delta2;

    Debug("Solve", 0);

    /* give global_delta a higher value then precision_goal */
    global_delta = 2 * precision_goal;

    while (global_delta > precision_goal && count < max_iter)
    {
        Debug("Do_Step 0", 0);
        delta1 = Do_Step(0);
        #ifdef SKIP_EXCHANGE
        if (count % skip_exchange == 0 && Exchange_Borders()) // use short circuit evaluation
        #endif
        #ifndef SKIP_EXCHANGE
        Exchange_Borders();
        #endif  
        Debug("Do_Step 1", 0);
        delta2 = Do_Step(1);
        #ifdef SKIP_EXCHANGE
        if (count % skip_exchange == 0 && Exchange_Borders())
        #endif
        #ifndef SKIP_EXCHANGE
        Exchange_Borders();
        #endif  
        delta = max(delta1, delta2);
        #ifdef MONITOR_ALLREDUCE
        double time_ = MPI_Wtime();
        #endif
        #ifdef ALLREDUCE_COUNT
        if(count % ALLREDUCE_COUNT == 0){
            MPI_Allreduce(&delta, &global_delta, 1, MPI_DOUBLE, MPI_MAX, grid_comm);
        }
        #endif
        #ifndef ALLREDUCE_COUNT
        MPI_Allreduce(&delta, &global_delta, 1, MPI_DOUBLE, MPI_MAX, grid_comm);
        #endif
        #ifdef MONITOR_ALLREDUCE
        all_reduce_time += MPI_Wtime() - time_;
        #endif
        #ifdef MONITOR_ERROR
        if (proc_rank == 0)
        {
            errors[count] = global_delta;
        }
        #endif
        count++;
    }

    printf("(%i) Number of iterations : %i\n", proc_rank, count);
    #ifdef MONITOR_ALLREDUCE
    printf("(%i) Allreduce time: %14.6f\n", proc_rank, all_reduce_time);
    #endif
    #ifdef MONITOR_EXCHANGE_BORDERS
    printf("(%i) Exchange time: %14.6f\n", proc_rank, total_exchange_time);
    #endif
}

double* get_Global_Grid()
{
    Debug("get_Global_Grid", 0);
    //!! DEBUG only
    for (size_t i = 0; i < dim[X_DIR]; i++)
    {
        for (size_t j = 0; j < dim[Y_DIR]; j++)
        {
            phi[i][j] = proc_rank;
        }
        
    }
    
    // only process 0 needs to store all data!
    double* global_phi = NULL;
    if (proc_rank == 0) {
        global_phi = malloc(gridsize[X_DIR] * gridsize[Y_DIR] * sizeof(double));
        if (global_phi == NULL) {
            Debug("get_Global_Grid : malloc(global_phi) failed", 1);
        }
    }

    // copy own part into buffer - flatten!
    size_t buf_size = (dim[X_DIR] - 2) * (dim[Y_DIR] - 2) * sizeof(double);
    double* local_phi = malloc(buf_size);
    int idx = 0;
    for (int x = 1; x < dim[X_DIR] - 1; x++) {
        for (int y = 1; y < dim[Y_DIR] - 1; y++) {
            local_phi[idx++] = phi[x][y];
        }
    }
    printf("I'm proc %d and i have a buffer of size %zu\n", proc_rank, buf_size);


    // only proc 0 needs sendcounts and displacements for the gatherv operation
    int* sendcounts = NULL;
    int* displs = NULL;
    if (proc_rank == 0) {
        sendcounts = malloc(P * sizeof(int));
        displs = malloc(P * sizeof(int));
        
        // size and offset of different subgrids
        //! Note that this only works if every process has the same subgrid
        if (gridsize[X_DIR] % P_grid[X_DIR] != 0 || gridsize[Y_DIR] % P_grid[Y_DIR] != 0)
        {
            Debug("!!!A grid dimension is not a multiple of the P_grid in this direction!", 1);
        }
        
        int subgrid_width = gridsize[X_DIR] / P_grid[X_DIR];
        int subgrid_height = gridsize[Y_DIR] / P_grid[Y_DIR];
        for (int px = 0; px < P_grid[X_DIR]; px++) {
            for (int py = 0; py < P_grid[Y_DIR]; py++) {
                int rank = px * P_grid[Y_DIR] + py;
                sendcounts[rank] = subgrid_width * subgrid_height;
                displs[rank] = (px * subgrid_width * gridsize[Y_DIR]) + (py * subgrid_height);
            }
        }
    }
    Debug("get_Global_Grid : MPI_Gatherv", 0);
    //! TODO this Gatherv does something wrong - all local grids are alright!!!
    MPI_Gatherv(local_phi, (dim[X_DIR] - 2) * (dim[Y_DIR] - 2), MPI_DOUBLE, global_phi, sendcounts, displs, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    free(local_phi);
    if (proc_rank == 0) {
        free(sendcounts);
        free(displs);
    }

    return global_phi;
}

void Write_Grid_global(){
    int x, y;
    FILE *f;
    char filename[40]; //seems danagerous to use a static buffer but let's go with the steps
    sprintf(filename, "output_MPI_global_%i.dat", proc_rank);
    if ((f = fopen(filename, "w")) == NULL){
        Debug("Write_Grid : fopen failed", 1);
    }

    Debug("Write_Grid", 0);

    for (x = 1; x < dim[X_DIR]-1; x++){
        for (y = 1; y < dim[Y_DIR]-1; y++){
            int x_glob = x + offset[X_DIR];
            int y_glob = y + offset[Y_DIR];
            fprintf(f, "%i %i %f\n", x_glob, y_glob, phi[x][y]);
        }
    }
    fclose(f);
}

void Write_Grid()
{
    double* global_phi = get_Global_Grid();
    if(proc_rank != 0){
        assert (global_phi == NULL);
        return;
    }
    int x, y;
    FILE *f;
    char filename[40]; //seems danagerous to use a static buffer but let's go with the steps
    sprintf(filename, "output_MPI%i.dat", proc_rank);
    if ((f = fopen(filename, "w")) == NULL){
        Debug("Write_Grid : fopen failed", 1);
    }

    Debug("Write_Grid", 0);

    for (x = 0; x < gridsize[X_DIR]; x++){
        for (y = 0; y < gridsize[Y_DIR]; y++){
            fprintf(f, "%i %i %f\n", x+1, y+1, global_phi[x*gridsize[Y_DIR] + y]);
        }
    }
    fclose(f);
    free(global_phi);
}

void Clean_Up()
{
    Debug("Clean_Up", 0);

    free(phi[0]);
    free(phi);
    free(source[0]);
    free(source);
    #ifdef MONITOR_ERROR
    free(errors);
    #endif
}
void setup_error_monitor(){
    if (proc_rank != 0)
    {
        return;
    }
    
    errors = malloc(sizeof(double)*max_iter);
}
void write_errors(){
    if(proc_rank != 0){
        return;
    }
    FILE *f;
    char filename[40]; //seems danagerous to use a static buffer but let's go with the steps
    sprintf(filename, "errors_MPI.dat");
    if ((f = fopen(filename, "w")) == NULL){
        Debug("Write_Errors : fopen failed", 1);
    }

    Debug("Write_Errors", 0);

    for (size_t i = 0; i < max_iter; ++i)
    {
        fprintf(f, "%f\n", errors[i]);
    }
    fclose(f);
}

void Print_Aggregated_Metrics()
{
    #ifdef MONITOR_EXCHANGE_BORDERS
    if (num_exchanges > 0) {
        double avg_exchange_time = total_exchange_time / num_exchanges;
        double avg_latency = total_latency / num_exchanges;
        double avg_bandwidth = total_data_transferred / total_exchange_time;

        printf("\n--- Aggregated Metrics ---\n");
        printf("Total Exchanges: %d\n", num_exchanges);
        printf("Total Data Transferred: %.2f bytes\n", total_data_transferred);
        printf("Total Exchange Time: %.9f s\n", total_exchange_time);
        printf("Average Exchange Time per Call: %.9f s\n", avg_exchange_time);
        printf("Average Latency per Call: %.9f s\n", avg_latency);
        printf("Average Bandwidth: %.2f bytes/s\n", avg_bandwidth);
    } else {
        printf("No exchanges recorded.\n");
    }
    #endif
}

int main(int argc, char **argv)
{
    MPI_Init(&argc, &argv);
    Setup_Proc_Grid(argc,argv); // was earlier MPI_Comm_rank(MPI_COMM_WORLD, &proc_rank);
    start_timer();

    Setup_Grid();
    Setup_MPI_Datatypes();

    #ifdef SOR
    if (proc_rank == 0)
    {
        printf("SOR using omega: %.5f\n", sor_omega);
    }
    #endif
    #ifdef MONITOR_ERROR
    setup_error_monitor();
    #endif

    Solve();
    #ifdef MONITOR_ERROR
    write_errors();
    #endif
    // Write_Grid();
    Write_Grid_global();
    Print_Aggregated_Metrics();
    print_timer();

    Clean_Up();
    MPI_Finalize();
    return 0;
}
