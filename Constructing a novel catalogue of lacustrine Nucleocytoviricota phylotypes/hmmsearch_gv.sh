#!/bin/bash

protein_path=$1
output_path=$2
database=$3
num_jobs=$4


# Check if the correct number of arguments is provided
if [ $# -ne 4 ]; then
echo "Usage: $0 <source_path> <target_path><database> <num_jobs>"
exit 1
fi

# Function to process a single gzip file
process_hmmsearch() {
local F="$1"

BASE=${F##*/}
SAMPLE=${BASE%%.*}
echo $SAMPLE

if [ -e $output_path/${SAMPLE}.txt ]; then
    echo "$SAMPLE SKIP"
else
    hmmsearch --tblout $output_path/${SAMPLE}.txt -E 1e-5 --cpu 80 $database $F
    echo "$SAMPLE hmmsearch DONE"
fi

}

# Use parallel to process gzip files in parallel with specified number of jobs
for F in $protein_path/*.faa; do
process_hmmsearch "$F" &
((++processed_files))
[ $((processed_files % num_jobs)) -eq 0 ] && wait
done

