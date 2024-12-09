#!/bin/bash
#SBATCH --job-name="grid_analysis"
#SBATCH --time=00:02:00  
#SBATCH --ntasks=12
#SBATCH --cpus-per-task=1
#SBATCH --partition=compute
#SBATCH --mem=2GB
#SBATCH --account=Education-EEMCS-Courses-WI4049TU

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <topology_x> <topology_y>"
    exit 1
fi

# Variables
topology_x=$1
topology_y=$2
basefolder="../scripts/output/1210/${topology_x}_${topology_y}"
mkdir -p $basefolder

# Define parameters
grids=("100 100" "200 200" "400 400" "800 800")
max_iter=50000
omega=1.93

# Move to src directory
cd ../src || { echo "Error: ../src directory not found"; exit 1; }

# Run computations for each grid size
for grid in "${grids[@]}"; do
    nx=$(echo $grid | cut -d' ' -f1)
    ny=$(echo $grid | cut -d' ' -f2)
    grid_folder="$basefolder/${nx}x${ny}"
    mkdir -p $grid_folder || { echo "Error creating grid directory"; exit 1; }

    # Update input.dat for the current grid
    python3 -c "
import util
util.update_input_file(nx=$nx, ny=$ny, max_iter=$max_iter)
" || { echo "Python script failed for nx=$nx, ny=$ny"; exit 1; }

    # Execute program
    output_file="$grid_folder/result.txt"
    echo "Running with nx=$nx, ny=$ny"
    srun ./MPI_Poisson.out $topology_x $topology_y $omega > $output_file || {
        echo "srun failed for nx=$nx, ny=$ny"; exit 1;
    }
    echo "Finished grid ${nx}x${ny}"
done

# Reset input.dat after all computations
python3 -c "
import util
util.reset_input_file()
" || { echo "Error resetting input file"; exit 1; }

echo "Job completed successfully."
