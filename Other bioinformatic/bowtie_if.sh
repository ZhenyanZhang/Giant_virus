#!/bin/bash

input_path=$1
output_path=$2
database=$3
listFile=$4
num_jobs=$5


# Check if the correct number of arguments is provided
if [ $# -ne 5 ]; then
echo "Usage: $0 <source_path> <target_path><database> <listFile> <num_jobs>"
exit 1
fi

# Function to process a single gzip file
process_bwa() {
local F="$1"

R=${F%_*}_2.fastq.gz
BASE=${F##*/}
SAMPLE=${BASE%_*}
echo $SAMPLE

if grep -qw "$SAMPLE" "$listFile"; then
	if [ -e $output_path/${SAMPLE}.bam ]; then
		echo "$SAMPLE SKIP"
	else
    		bowtie2 -p 50 --sensitive -x $database -1 $F -2 $R | samtools sort -@ 14 -o $output_path/${SAMPLE}.bam
    		echo "$SAMPLE bowtie DONE"
    	fi
else
	echo "$SAMPLE SKIP"
fi

}

# Use parallel to process gzip files in parallel with specified number of jobs
for F in $input_path/*_1.fastq.gz; do
process_bwa "$F" &
((++processed_files))
[ $((processed_files % num_jobs)) -eq 0 ] && wait
done

