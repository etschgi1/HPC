#!/bin/bash
#SBATCH --job-name="scaling_analysis"
#SBATCH --time=00:02:00  
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --partition=compute
#SBATCH --mem=2GB
#SBATCH --account=Education-EEMCS-Courses-WI4049TU

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <topology_x> <topology_y>"
    exit 1
fi

# Variables
basefolder="../scripts/output/128/${1}_${2}"
mkdir -p $basefolder

# Define parameters
grids=("100 100" "200 200" "400 400")
skips=("1" "2" "5" "10" "25" "50")
max_iter=50000
omega=1.93

# Move to src directory
cd ../src || { echo "Error: ../src directory not found"; exit 1; }

# Run computations
for grid in "${grids[@]}"; do
    nx=$(echo $grid | cut -d' ' -f1)
    ny=$(echo $grid | cut -d' ' -f2)
    grid_folder="$basefolder/${nx}x${ny}"
    mkdir -p $grid_folder || { echo "Error creating grid directory"; exit 1; }

    for skip in "${skips[@]}"; do
        # Update input.dat
        python3 -c "
import util
util.update_input_file(nx=$nx, ny=$ny, max_iter=$max_iter)
" || { echo "Python script failed for nx=$nx, ny=$ny"; exit 1; }

        # Execute program
        output_file="$grid_folder/skip_${skip}.txt"
        echo "Running with nx=$nx, ny=$ny, skip=$skip"
        srun ./MPI_Poisson.out $1 $2 $omega $skip > $output_file || {
            echo "srun failed for nx=$nx, ny=$ny, skip=$skip"; exit 1;
        }
        echo "Finished skip=$skip for grid ${nx}x${ny}"
    done
done

# Reset input.dat
python3 -c "
import util
util.reset_input_file()
" || { echo "Error resetting input file"; exit 1; }

echo "Job completed successfully."
