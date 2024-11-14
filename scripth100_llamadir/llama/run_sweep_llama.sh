#!/bin/bash

# Arrays of different options

#export OMPI_ALLOW_RUN_AS_ROOT=1
#export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1 
declare -a max_output_lens=("32" )
#declare -a input_tokens=("16" "24" "48" "96" "256" "512" "1024" "2048") 
declare -a input_tokens=("256") 
declare -a batch_sizes=("1")

# Print header
#echo "max_output_len, input_token, batch_size, avg_latency," >> report.csv
echo "max_output_len, input_token, batch_size, avg_latency," >> reportllama3_8B.csv

# Run iterations
for max_output_len in "${max_output_lens[@]}"; do
    for input_token in "${input_tokens[@]}"; do
        for batch_size in "${batch_sizes[@]}"; do
            echo "Running with max_output_len=${max_output_len}, input_token=${input_token}, batch_size=${batch_size}"
            # Run the command and capture the output
            #cmd="mpirun -n 2 python3 ../run.py --engine_dir ./trt_engines/mixtral/tp2 --tokenizer_dir /model/mixtral/Mixtral-8x7B-v0.1 --max_output_len ${max_output_len} --promptfile input.json --input_token ${input_token} --batch_size ${batch_size} --max_attention_window_size  ${input_token} --max_input_length ${input_token}  --run_profiling"
            #cmd="python3 ../run.py --engine_dir  ./tmp/llama/13B/trt_engines/bf16/1-gpu/ --tokenizer_dir  /Llama-2-13b-hf --max_output_len ${max_output_len} --promptfile input.json --input_token ${input_token} --batch_size ${batch_size} --max_attention_window_size  ${input_token} --max_input_length ${input_token}  --run_profiling"
            cmd="python3 ../run.py --engine_dir  ./tmp/llama/8B/trt_engines/bf16/1-gpu/ --tokenizer_dir  /code/tensorrt_llm/Meta-Llama-3-8B/ --max_output_len ${max_output_len} --promptfile input.json --input_token ${input_token} --batch_size ${batch_size} --max_attention_window_size  ${input_token} --max_input_length ${input_token}  --run_profiling"
	    echo "$cmd"
	    output=$(${cmd})
            
            # Extract the average latency from the output
            avg_latency=$(echo "${output}" | grep -oP 'inftime=\K[0-9.]+(?=\s+sec)')
            
            # Check if we got a latency result
            if [ ! -z "$avg_latency" ]; then
                # Print the results
                echo "${max_output_len}, ${input_token}, ${batch_size}, ${avg_latency}" >> reportllama3_8B.csv
            else
                echo "No latency result found for max_output_len=${max_output_len}, input_token=${input_token}, batch_size=${batch_size}"
            fi
        done
    done
done

