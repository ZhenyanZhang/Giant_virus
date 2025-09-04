#!/bin/bash

#make important folders
#clean data after fastp
mkdir cleandata
#contigs after assembly
mkdir contigs
#all sequences of contigs (both protein and nucl)
mkdir protein
#hmmsearch results of polB sequences
mkdir hmmsearch
#polB sequences (both protein and nucl)
mkdir hmm_seq


#gene prediction for contigs
bash prodigal_for_gv.sh contigs protein 100

#hmmsearch polB from contigs
bash hmmsearch_gv.sh protein hmmsearch NCLDV_PolB.hmm 100

#extract polB from contigs (both protein and nucl)
bash hmm_extract_seq.sh protein hmmsearch hmm_seq 100

#add sample name into each sequence (both prot and nucl)
bash add_filename_into_fa.sh hmm_seq 50
bash add_filename_into_fa_nucl.sh hmm_seq 50

#merge sequences of polB (both prot and nucl)
cat hmm_seq/*_polb.protein.faa > polb_lake.protein.fa
cat hmm_seq/*_polb.nucl.fa > polb_lake.nucl.fa

#dereplicate protein sequences of polB
cd-hit -i polb_lake.protein.fa -o polb_lake.protein.derep.fa -c 0.95 -M 0 -T 200 -aS 0.9

#merge polB sequences in this study and referenece sequences in Microbiome
cat polb_lake.protein.derep.fa ref_id.faa > all_polb_ref.fasta

#alin polB sequences
mafft --thread 250 --6merpair --addfragments all_polb_ref.fasta pplacer_ref211.msa > all_polb_ref_comb.fasta

#place polB sequences into reference tree
pplacer -j 250 --verbosity 2 --keep-at-most 1 -o all_polb_ref_comb.fasta.jplace -t RAxML_bestTree.PolB_Ref_pplacer_mid -s RAxML_info.PolB_Ref_pplacer_mid all_polb_ref_comb.fasta

#add family name for each refrence sequences
sh sed_family.sh all_polb_ref_comb.fasta.jplace
sh sed2_family.sh all_polb_ref_comb.fasta.jplace

#jplace file to list
python pplacer_grep.py all_polb_ref_comb.fasta.jplace

#extract GV-polB
seqtk subseq polb_lake.protein.derep.fa all_polb_ref_comb.fasta.jplace.NCLDV > NCLDV_polb_lake.prot.faa
seqtk subseq polb_lake.nucl.fa all_polb_ref_comb.fasta.jplace.NCLDV > NCLDV_polb_lake.nucl.fa

#bwa index
bwa index NCLDV_polb_lake.nucl.fa



