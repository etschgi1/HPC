#!/bin/bash

# Check total entries in the queue
total_entries=$(squeue | wc -l)
echo "Total queue entries: $((total_entries - 1))" # Subtract header line

# Get your username
username=$(whoami)
echo "User: $username"

# Get the earliest job's ID in the queue
earliest_job=$(squeue | awk 'NR==2 {print $1}') # Skip the header line

# Get your jobs in the queue (include header)
my_jobs=$(squeue --me) # This includes all info including the header

# Get your first job's ID
my_first_job=$(squeue --me | awk 'NR==2 {print $1}') # Your earliest job ID

# Compute distance of your job from the earliest
if [[ -z $my_first_job ]]; then
    echo "You have no jobs in the queue."
else
    # Find position of your first job relative to the earliest job
    distance_to_first=$(squeue | awk -v my_job="$my_first_job" '{if ($1 == my_job) print NR-1}')
    echo "Your first job (ID: $my_first_job) is $distance_to_first positions from the earliest job in the queue."
fi

# List your scheduled jobs (including header)
echo "Your scheduled jobs (with header):"
echo "$my_jobs"
