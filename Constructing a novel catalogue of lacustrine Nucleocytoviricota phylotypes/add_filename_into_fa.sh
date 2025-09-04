#!/bin/bash

# Function to process a single gzip file
process_add_name() {
local file="$1"
echo $file

awk -v fname=$(basename $file .fna) '/^>/ {print ">" fname "~" substr($0, 2)} !/^>/ {print $0}' $file > $(basename $file .fna)_temp.fna && mv $(basename $file .fna)_temp.fna $file

}

# Check if the correct number of arguments is provided
if [ $# -ne 2 ]; then
echo "Usage: $0 <source_path><num_jobs>"
exit 1
fi

folder_path=$1
num_jobs=$2


# Find all gzip files in the folder
gzip_files=("$folder_path"/*.fna)

# Use parallel to process gzip files in parallel with specified number of jobs
for file in "${gzip_files[@]}"; do
process_add_name "$file" &
((++processed_files))
[ $((processed_files % num_jobs)) -eq 0 ] && wait
done

wait

echo "Done all fastq"
