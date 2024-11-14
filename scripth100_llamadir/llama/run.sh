#!/bin/bash
#nvidia-cuda-mps-control -d
CUDA_VISIBLE_DEVICES=0 python3 ../run_tmp.py --engine_dir  ./tmp/llama/8B/trt_engines/bf16/1-gpu/ --tokenizer_dir  /code/tensorrt_llm/Meta-Llama-3-8B/ --max_output_len 128 --promptfile input.json --input_token 512 --batch_size 1 --max_attention_window_size 512  --max_input_length 512  --run_profiling &
CUDA_VISIBLE_DEVICES=1 python3 ../run_tmp.py --engine_dir  ./tmp/llama/8B/trt_engines/bf16/1-gpu/ --tokenizer_dir  /code/tensorrt_llm/Meta-Llama-3-8B/ --max_output_len 128 --promptfile input.json --input_token 512 --batch_size 1 --max_attention_window_size 512  --max_input_length 512  --run_profiling

#echo quit | nvidia-cuda-mps-control
