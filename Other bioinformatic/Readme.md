# Script for bioinformatic

## Quality-filter
bash Meta_qc_multi.sh raw_data clean_data 5

## Assembly
bash assembly_multi.sh clean_data contigs 5

## Constructing a catalogue of lacustrine Nucleocytoviricota phylotypes
Scripts for this step can be found in [Constructing a catalogue of lacustrine Nucleocytoviricota phylotypes](../Constructing a catalogue of lacustrine Nucleocytoviricota phylotypes)

## Mapping the Nucleocytoviricota phylotypes in the lacustrine samples
bash bowtie_if.sh clean_data results_bowtie gv_polB.fna lake_list.txt 5

## Calculating the abundance of Nucleocytoviricota phylotypes in the lacustrine samples
bash bam_to_abundance.sh results_bowtie 0.5 abundance_for_gv_polb
