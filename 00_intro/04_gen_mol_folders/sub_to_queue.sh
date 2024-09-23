#!/bin/bash
#
#SBATCH --job-name="gen_mol"
#SBATCH --time=00:03:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --partition=compute
#SBATCH --mem=1GB
#SBATCH --account=Education-EEMCS-Courses-WI4049TU
#SBATCH --reservation=wi4049tu
#SBATCH --qos=reservation

# Run Python script:
module load 2023r1
module load python
module load py-numpy
module load py-scipy
module load py-matplotlib

srun python gen_mol_folders.py
