# Intro to Delft Blue

Documentation
https://doc.dhpc.tudelft.nl/delftblue/

There is also a Mattermost

There are also trainings and courses!

## SSH: secure shell

```bash
ssh tbvanderwoude@student-linux.tudelft.nl
ssh tbvanderwoude@login.delftblue.tudelft.nl
```

## Home and scratch

Home is backed up. Scratch is temporary storage for big simulations.

## SLURM basics

How busy is the system: `squeue`

How many jobs in the queue:
`squeue | wc -l`

`|` feeds the `squeue` output into `wc -l`. 

Running small jobs however is fine! Most jobs just need a lot of resources.

Workflow:

1. Prepare and upload code and files
2. Determine resources
3. Submit job script

Be realistic with resource estimates (especially time!). It makes scheduling your jobs far easier and faster. Does it run longer? It will be terminated. Will it be ~4 hours? Ask for 6.

SLURM script only gives you what you need, making the code it runs parallel is up to you (using MPI and mpirun etc.)

You submit your script using `sbatch jobscript.sh`

You can see the output using `cat slurm-1.out`

You can see just your jobs using `squeue --me`. `scancel` will cancel your job. 

The slurm output file will contain all the standard output from the script

## Parallelism

Shared memory: a single processor using multiple cores on the same memory.

Translates neatly to a single process matching the number of cores with multithreading.

Supercomputer: distributed memory parallelism, requires message passing between different instances.

## Module system

To show modules that are available

```bash
module avail
```

Out of the box almost no software is available! You can `load` and `unload`, which will also change what is available. 

Almost everything is there as a module!

To learn where things (say PyTorch) are available

```
module spider torch
```

## Execution workflow

Your job will load the modules you add after resource allocation. The script is only allocated once by a worker with all the needed resources. `srun` runs something in a way so that all resources can be used by the binary/script.

Task number matches MPI processes?

GPU nodes require a specific partition: `gpu-a100-small`. You also still have to ask for gpus per task. 

squeue | grep Torch 