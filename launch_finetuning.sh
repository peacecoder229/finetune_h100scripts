#!/bin/bash

# Set the number of OpenMP threads
export OMP_NUM_THREADS=64

# Ensure no GPUs are used
export CUDA_VISIBLE_DEVICES=

# Use taskset to bind the processes to specific CPU cores
#ONEDNN_VERBOSE=1 taskset -c 0-63,64-127 accelerate launch --config_file=config_cpu.yaml finetune.py
taskset -c 0-63,64-127 accelerate launch --config_file=config_cpu.yaml finetune.py
