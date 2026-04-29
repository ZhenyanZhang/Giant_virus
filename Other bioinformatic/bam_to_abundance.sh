#!/bin/bash

# Check if correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <BAM_DIR> <BREADTH_CUTOFF> <OUT_DIR>"
    echo "Example: $0 ./bam_files 0.50 ./Final_Results_PolB"
    exit 1
fi

# ================= Configuration =================
INPUT_DIR="$1"       # Path to directory containing .bam files
BREADTH_CUTOFF="$2"  # Breadth coverage threshold (e.g., 0.50)
OUT_DIR="$3"         # Path to output directory

TARGET_DEPTH=100000000

COUNTS_FILE="depth_counts.txt"

SMALL_SAMPLE_FILE="small_sample_0.5.txt"

mkdir -p "$OUT_DIR"
# ===============================================

echo "=== Step 1: Initialization & checking input files ==="

if [ ! -f "$COUNTS_FILE" ]; then
    echo "Error: $COUNTS_FILE not found!"
    exit 1
fi

echo "Target Rarefaction Depth: $TARGET_DEPTH"
echo "Breadth Cutoff: $BREADTH_CUTOFF"
echo "Check Output Exists: YES (Resume Mode)"
echo "------------------------------------------------------"

echo "=== Step 2: Processing Loop ==="

for bam in "${INPUT_DIR}"/*.bam; do
    [ -e "$bam" ] || continue
    
    SAMPLE=$(basename "$bam" .bam)
    
    # --- ???????????????ļ??Ƿ????? (?ϵ??????߼?) ---
    FINAL_STATS="${OUT_DIR}/${SAMPLE}.final_stats.txt"
    
    if [ -f "$FINAL_STATS" ]; then
        echo "[Skipping $SAMPLE] Output already exists."
        continue
    fi
    # -----------------------------------------------

    echo "[Processing $SAMPLE]"

    # --- 2.0 Get Current Depth ---
    CURRENT_DEPTH=$(grep "$bam" "$COUNTS_FILE" | awk '{print $2}')

    if [ -z "$CURRENT_DEPTH" ]; then
        echo "  Warning: Depth not found for $bam. Skipping."
        continue
    fi

    # --- 2.1 Check Depth Threshold ---
    if [ "$CURRENT_DEPTH" -lt "$TARGET_DEPTH" ]; then
        echo "  -> Skipped: Depth $CURRENT_DEPTH < $TARGET_DEPTH"
        # ʹ??׷??ģʽ >>?????⸲??
        echo -e "${SAMPLE}\t${CURRENT_DEPTH}" >> "$SMALL_SAMPLE_FILE"
        continue
    fi

    # --- 2.2 Calculate Subsampling Factor ---
    FACTOR=$(awk -v t="$TARGET_DEPTH" -v c="$CURRENT_DEPTH" 'BEGIN {printf "%.6f", t/c}')
    SUBSAMPLE_PARAM="100${FACTOR}"
    
    echo "  -> Subsampling Factor: $FACTOR"

    # --- 2.3 Physical Subsampling AND Sorting ---
    TEMP_BAM="${OUT_DIR}/${SAMPLE}.temp.bam"

    samtools view -@ 64 -s "$SUBSAMPLE_PARAM" -b "$bam" | samtools sort -@ 64 - -o "$TEMP_BAM"
    samtools index -@ 64 "$TEMP_BAM"

    # --- 2.4 Quantification with CoverM ---
    COVERM_RAW="${OUT_DIR}/${SAMPLE}.coverm_raw.txt"
    
    echo "  -> Running CoverM (Contig Mode)..."
    
    coverm contig \
        --bam-files "$TEMP_BAM" \
        --output-format sparse \
        --methods trimmed_mean covered_fraction count \
        --trim-min 5 --trim-max 95 \
        --min-covered-fraction 0 \
        --output-file "$COVERM_RAW"

    # --- 2.5 Apply Breadth Threshold (Filtering via AWK) ---
 awk -v cutoff="$BREADTH_CUTOFF" -F'\t' '
    NR==1 {print $0}      # Print header
    NR>1 {
        # Col 4 is Covered Fraction
        if ($4 >= cutoff) print $0
    }' "$COVERM_RAW" > "$FINAL_STATS"

    # --- 2.6 Clean up ---
    rm "$TEMP_BAM" "${TEMP_BAM}.bai" "$COVERM_RAW"
    
    echo "  -> Done. Saved to $FINAL_STATS"
done

echo "=== All Analysis Finished ==="
echo "Skipped samples are listed in: $SMALL_SAMPLE_FILE"