#!/bin/bash

MASTER_LIST="/beegfs/dataset/master_list.txt"
BATCH_SIZE=100

# 1. Count the total number of lines in the text file
TOTAL_FILES=$(wc -l < "$MASTER_LIST")

# 2. Calculate how many chunks we need
# We use Bash integer math to round up (ceiling division)
TOTAL_CHUNKS=$(( (TOTAL_FILES + BATCH_SIZE - 1) / BATCH_SIZE ))

# 3. Slurm arrays start at 0, so the max index is chunks - 1
MAX_INDEX=$(( TOTAL_CHUNKS - 1 ))

echo "Dataset analysis complete:"
echo "- Total Files: $TOTAL_FILES"
echo "- Batch Size : $BATCH_SIZE"
echo "- Array Range: 0 to $MAX_INDEX"

# 4. Inject the dynamic array directly into the sbatch command!
sbatch --array=0-$MAX_INDEX submit_bash_parallel.sh