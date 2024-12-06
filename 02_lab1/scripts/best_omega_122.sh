#!/bin/bash
#SBATCH --job-name="best_omega"
#SBATCH --time=00:02:00
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --partition=compute
#SBATCH --mem=1GB
#SBATCH --account=Education-EEMCS-Courses-WI4049TU

cd ../src

omegas=$(python3 -c "import numpy as np; print(' '.join(map(str, np.linspace(1.75, 2, 25))))")

mkdir -p ../scripts/output/122

# Loop over omegas and run the program for each value
for omega in $omegas; do
    echo "Running with omega=$omega"
    srun ./MPI_Poisson.out 4 1 $omega > ../scripts/output/122/omega_${omega}.txt
    echo "Finished omega=$omega"
done

# Notify job completion
echo "Job completed successfully."