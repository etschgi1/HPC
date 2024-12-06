#!/bin/bash
#SBATCH --job-name=mpi_poisson_batch   # Job name
#SBATCH --output=output_%j.log         # Standard output and error log
#SBATCH --ntasks=4                     # Total number of tasks (adjust as needed)
#SBATCH --cpus-per-task=1              # Number of CPUs per task
#SBATCH --mem-per-cpu=1G               # Memory per CPU
#SBATCH --time=00:00:45                # Time limit (adjust as necessary)
#SBATCH --account=Education-EEMCS-Courses-WI4049TU

nx=$1
ny=$2
g=$3
python3 gen_input.py $g $g 1 > input.dat
./go 4 mpi_poisson $nx $ny
python3 gen_input.py $g $g 96 > input.dat
./go 4 mpi_poisson $nx $ny
python3 gen_input.py $g $g 191 > input.dat
./go 4 mpi_poisson $nx $ny
python3 gen_input.py $g $g 287 > input.dat
./go 4 mpi_poisson $nx $ny
python3 gen_input.py $g $g 382 > input.dat
./go 4 mpi_poisson $nx $ny