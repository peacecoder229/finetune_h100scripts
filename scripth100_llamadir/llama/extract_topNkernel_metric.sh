#!/bin/bash

# Define the temporary directory for storing CSV files

inputfile=$1
metric=$2
topn=$3
temp_dir="temp_csv_files"

echo "Extracting $metric and for topn $topn"

# Create temporary directory if it doesn't already exist
mkdir -p "$temp_dir"

# Initial call to get unique kernel names and their respective outputs
output=$(./process_filter_csvfiles.py --rule "Metric Name: == '${metric}'" --inputfile $inputfile --applyrulefirst --printcol "Kernel Name" --sortcol '{"Metric Value": "desc"}' --topn $topn)

echo "$output"

# Extract unique kernel names and process each
echo "$output" | jq -r 'map(.["Kernel Name"]) | unique[]' | while read -r kernel_name
do
    echo "Processing kernel name: $kernel_name"

    # Run the Python script for each unique kernel name and capture the output
    json_output=$(./process_filter_csvfiles.py --rule "Kernel Name: contains '$kernel_name',&,Device: ==0" --inputfile $inputfile --extraprintcols "Metric Unit")
    echo "${json_output}" >> LOG

    # Filter out non-JSON lines (e.g., debug messages) and process with jq
    filtered_json_output=$(echo "${json_output}" | sed -n '/^\[/,$p')

    if [[ ! -z "$filtered_json_output" ]]; then
        # Convert JSON to CSV and save it in the temporary directory
        csv_file="${temp_dir}/${kernel_name// /_}_metrics.csv"
        echo "$filtered_json_output" | jq -r --arg kn "$kernel_name" '
            ["'${kernel_name}_met'","'${kernel_name}_val'","'${kernel_name}_unit'"],
            (.[] | [.["Metric Name"], .["Metric Value"], .["Metric Unit"] | tostring])
            | @csv
        ' > "$csv_file"

        echo "Metrics processed and saved for $kernel_name in $csv_file"
    else
        echo "No valid JSON output for $kernel_name"
    fi
done

# Define final CSV filename after removing all spaces from $metric
met=$(echo "$metric" | sed 's/[[:space:]]//g')
final_csv="${inputfile}_${met}_topN${topn}.csv"


echo "$met and $final_csv"
# Check if any CSV files exist to concatenate
csv_files=($(ls ${temp_dir}/*.csv))
if [ ${#csv_files[@]} -gt 0 ]; then
    # Use paste to concatenate all CSV files horizontally
    paste -d ',' "${csv_files[@]}" > "$final_csv"
    echo "All metrics have been combined into $final_csv"
else
    echo "No CSV files were generated to combine."
fi

rm -rf "$temp_dir"

# Optionally, clean up by removing the temporary directory
# rm -rf "$temp_dir"

