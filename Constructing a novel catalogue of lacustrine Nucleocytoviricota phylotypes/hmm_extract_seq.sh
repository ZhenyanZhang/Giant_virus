#!/bin/bash

seq_path=$1
hmm_path=$2
hmm_seq=$3
num_jobs=$4


# Check if the correct number of arguments is provided
if [ $# -ne 4 ]; then
echo "Usage: $0 <seq_path> <hmm_path><hmm_seq> <num_jobs>"
exit 1
fi

# Function to process a single gzip file
process_hmm_extract_seq() {
local F="$1"

BASE=${F##*/}
SAMPLE=${BASE%.*}
echo $SAMPLE

if [ -e $hmm_seq/${SAMPLE}.done ]; then
    echo "$SAMPLE SKIP"
else
    grep -v "^#" $F | awk '{print $1}' | sort | uniq > $hmm_seq/${SAMPLE}_matched_ids.txt
    seqtk subseq $seq_path/${SAMPLE}.protein.faa $hmm_seq/${SAMPLE}_matched_ids.txt > $hmm_seq/${SAMPLE}_polb.protein.faa
    echo "$SAMPLE hmmsearch DONE" > $hmm_seq/${SAMPLE}.done
fi

}

# Use parallel to process gzip files in parallel with specified number of jobs
for F in $hmm_path/*.txt; do
process_hmm_extract_seq "$F" &
((++processed_files))
[ $((processed_files % num_jobs)) -eq 0 ] && wait
done

