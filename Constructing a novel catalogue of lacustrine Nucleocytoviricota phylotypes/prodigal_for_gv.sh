#!/bin/bash

input_path=$1
output_path=$2
num_jobs=$3

# Function to process a single file
process_prodigal() {
    local F="$1"
    BASE=${F##*/}
    SAMPLE=${BASE%%.*}
    echo $SAMPLE
    if [ -e $output_path/${SAMPLE}.done ]; then
        echo "already prodigal, skip"
    else
        prodigal -i $F -a $output_path/${SAMPLE}.protein.faa -d $output_path/${SAMPLE}.nucl.fa -o $output_path/${SAMPLE}.gff -f gff -p meta
        echo "$SAMPLE prodigal done"
        echo "$SAMPLE prodigal done" > $output_path/${SAMPLE}.done
    fi
}

for F in $input_path/*.contigs.fa; do
process_prodigal "$F" &
((++processed_files))
[ $((processed_files % num_jobs)) -eq 0 ] && wait
done

wait

