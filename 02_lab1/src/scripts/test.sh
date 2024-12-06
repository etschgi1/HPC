#!/bin/bash

# Slurm directives
#SBATCH --job-name="test_job"           # Job name
#SBATCH --partition=compute              # Partition (queue) name
#SBATCH --time=00:00:15                  # Runtime limit (HH:MM:SS)
#SBATCH --ntasks=4                       # Total number of tasks
#SBATCH --cpus-per-task=1                # Number of CPUs per task
#SBATCH --mem-per-cpu=500M               # Memory per CPU
#SBATCH --output=test_output/job_%j.out  # Output file
#SBATCH --error=test_output/job_%j.err   # Error file
#SBATCH --account=Education-EEMCS-Courses-WI4049TU
#SBATCH --reservation=wi4049tu

# Load necessary modules
module load 2024r1 openmpi

# Change to the directory where the script is located
cd "$(dirname "$0")"

# Create output directory if it doesn’t exist
mkdir -p test_output || { echo "Failed to create output directory"; exit 1; }

# Run a simple test command
echo "Hello, this is a test job!" > test_output/hello_world.txt

# Notify job completion
echo "Test job completed successfully."