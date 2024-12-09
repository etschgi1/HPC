#!/bin/bash
#SBATCH --job-name="scaling_123"
#SBATCH --time=00:03:00  
#SBATCH --ntasks=9
#SBATCH --cpus-per-task=1
#SBATCH --partition=compute
#SBATCH --mem=2GB  # Increased memory
#SBATCH --account=Education-EEMCS-Courses-WI4049TU

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <topology_x> <topology_y>"
    exit 1
fi

# Move to the src directory
cd ../src || { echo "Error: ../src directory not found"; exit 1; }
basefolder="1211/${1}_${2}"
mkdir -p ../scripts/output/$basefolder || { echo "Error creating output directory"; exit 1; }

# Define maximum iterations and grid sizes
grids=("200 200" "400 400" "800 800" "1600 1600" "3200 3200")

for grid in "${grids[@]}"; do
    nx=$(echo $grid | cut -d' ' -f1)
    ny=$(echo $grid | cut -d' ' -f2)

    mkdir -p ../scripts/output/$basefolder/${nx}x${ny} || { echo "Error creating grid directory"; exit 1; }
    python3 -c "
import util
util.update_input_file(nx=$nx, ny=$ny, precision_goal=0.0001, max_iter=5000)
" || { echo "Python script failed for nx=$nx, ny=$ny, max_iter=5000"; exit 1; }

    echo "Running with nx=$nx, ny=$ny, maxiter=5000"
    srun ./MPI_Poisson.out $1 $2 1.95 > ../scripts/output/$basefolder/${nx}x${ny}/output.txt || {
        echo "srun failed for nx=$nx, ny=$ny, max_iter=5000"; exit 1; 
    }
    echo "Finished maxiter=5000 for grid ${nx}x${ny}"
done

python3 -c "
import util
util.reset_input_file()
" || { echo "Error resetting input file"; exit 1; }

echo "Job completed successfully."
