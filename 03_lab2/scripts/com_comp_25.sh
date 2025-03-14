#!/bin/bash
#SBATCH --job-name="com_comp"
#SBATCH --time=00:03:00  
#SBATCH --ntasks=4
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
basefolder="25/${1}_${2}"
mkdir -p ../scripts/output/$basefolder || { echo "Error creating output directory"; exit 1; }

grids=("10 10" "20 20" "30 30" "35 35" "40 40" "50 50" "75 75" "84 84" "90 90")

for grid in "${grids[@]}"; do
    nx=$(echo $grid | cut -d' ' -f1)
    ny=$(echo $grid | cut -d' ' -f2)

    mkdir -p ../scripts/output/$basefolder/${nx}x${ny} || { echo "Error creating grid directory"; exit 1; }

    echo "Running pre-script: ./GridDist.out"
    ./GridDist.out $1 $2 $nx $ny || { echo "Pre-script failed"; exit 1; }
    echo "Pre-script completed successfully."

    echo "Running with nx=$nx, ny=$ny, maxiter=5000"
    srun ./MPI_Fempois.out > ../scripts/output/$basefolder/${nx}x${ny}/output.txt || {
        echo "srun failed for nx=$nx, ny=$ny, max_iter=5000"; exit 1; 
        }
    echo "Finished maxiter=5000 for grid ${nx}x${ny}"
done

echo "Job completed successfully."
