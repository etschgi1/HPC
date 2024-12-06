#!/bin/bash
#SBATCH --job-name="scaling_123"
#SBATCH --time=00:03:00
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --partition=compute
#SBATCH --mem=1GB
#SBATCH --account=Education-EEMCS-Courses-WI4049TU

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <topology_x> <topology_y>"
    exit 1
fi


# Move to the src directory
cd ../src
basefolder="${1}_${2}"
# Ensure output directory exists
mkdir -p ../scripts/output/$basefolder

# Generate omega values using Python
maxiters=("500" "1000" "2000")

# Define grid sizes for testing
grids=("50 50" "100 100" "200 200")

# Loop over grids
for grid in "${grids[@]}"; do
    nx=$(echo $grid | cut -d' ' -f1)
    ny=$(echo $grid | cut -d' ' -f2)

    # Create subdirectory for this grid size
    mkdir -p ../scripts/output/$basefolder/${nx}x${ny}


    # Loop over omegas
    for maxiter in $maxiters; do
    # Update input.dat using util.py
            python3 -c "
        import util
        util.update_input_file(nx=$nx, ny=$ny, precision_goal=0.000000000000001, max_iter=$maxiter)
        "
        echo "Running with nx=$nx, ny=$ny, maxiter=$maxiter"
        srun ./MPI_Poisson.out $1 $2 1.95 > ../scripts/output/$basefolder/${nx}x${ny}/maxiter_${maxiter}.txt
        echo "Finished maxiter=$maxiter for grid ${nx}x${ny}"
    done
done

    # Reset input.dat using util.py
    python3 -c "
import util
util.reset_input_file()
"

# Notify job completion
echo "Job completed successfully."
