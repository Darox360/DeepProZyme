#!/bin/bash

input_file="./data/new.fa"
output_dir="./results"
gpu_device="cuda:0"
batch_size=128
cpu_cores=2

# 运行DeepECTransformer
python run_deepectransformer.py \
    -i $input_file \
    -o $output_dir \
    -g $gpu_device \
    -b $batch_size \
    -cpu $cpu_cores
