#!/bin/bash

#bash ~/meta_script/Meta_qc_multi.sh rawdata qc_data xxx
input_path=$1
output_path=$2
num_jobs=$3

# Check if the correct number of arguments is provided
if [ $# -ne 3 ]; then
echo "Usage: $0 <source_path> <target_path> <num_jobs>"
exit 1
fi

# Function to process a single gzip file
process_QC() {
local F="$1"

R=${F%_*}_2.fastq.gz
BASE=${F##*/}
SAMPLE=${BASE%_*}
echo $SAMPLE

if [ -e $output_path/html/${SAMPLE}.html ]; then
    echo "$BASE SKIP"
else
    fastp -i $F -I $R -o $output_path/${SAMPLE}_1.fastq.gz -O $output_path/${SAMPLE}_2.fastq.gz -w 16 -h $output_path/html/${SAMPLE}.html -j $output_path/json/${SAMPLE}.json
    echo "$BASE fastp DONE"
fi

}

# Use parallel to process gzip files in parallel with specified number of jobs
for F in $input_path/*_1.fastq.gz; do
process_QC "$F" &
((++processed_files))
[ $((processed_files % num_jobs)) -eq 0 ] && wait
done

wait

