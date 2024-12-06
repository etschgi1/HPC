#!/bin/bash
#SBATCH --job-name="best_omega"
#SBATCH --time=00:02:00
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --partition=compute
#SBATCH --mem=1GB
#SBATCH --account=Education-EEMCS-Courses-WI4049TU

cd ..
# Loop over omegas and run the program for each value
for omega in $omegas; do
    echo "Running with omega=$omega"
    srun ../MPI_Poisson.out 4 1 $omega > output/omega_${omega}.txt
    echo "Finished omega=$omega"
done
# for omega in $omegas; do
#     echo "Running with omega=$omega" >> debug.log
#     srun ../MPI_Poisson.out 4 1 $omega >> debug.log 2>&1
#     echo "Finished omega=$omega" >> debug.log
# done
# Notify job completion
echo "Job completed successfully."