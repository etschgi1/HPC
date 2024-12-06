#!/bin/bash
#
#SBATCH --job-name=test_job          # Name of the job
#SBATCH --partition=compute          # Partition to submit to
#SBATCH --time=00:10:00              # Maximum runtime (10 minutes)
#SBATCH --ntasks=1                   # Number of tasks (1)
#SBATCH --cpus-per-task=1            # Number of CPUs per task
#SBATCH --mem-per-cpu=1G             # Memory per CPU (1 GB)
#SBATCH --output=test_output.%j.out  # Output file (%j is the job ID)
#SBATCH --error=test_output.%j.err   # Error file
#SBATCH --account=Education-EEMCS-Courses-WI4049TU

# Load any required modules (if needed)
module load 2024r1 openmpi 

# Run a simple command or script
echo "Running a test job on DelftBlue"
echo "Hello, World!" > hello_world.txt
