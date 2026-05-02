#!/bin/bash

MASTER_LIST="/beegfs/dataset/demo_master_list.txt"
BATCH_SIZE=10

echo "Cleaning up old data for a fresh capacity test..."
rm -f /beegfs/almalinux/chunk_*.out
rm -f /beegfs/dataset/results.db

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

# 4. Submit the dynamic array and capture its ID!
# --parsable tells Slurm to only print the Job ID number
ARRAY_JOB_ID=$(sbatch --parsable --array=0-$MAX_INDEX submit_bash_parallel.sh)

echo "Array Job Submitted with ID: $ARRAY_JOB_ID"

# 5. Submit the Aggregator job with a strict dependency
# 'afterany' ensures it runs after the array finishes, even if some chunks fail
AGG_JOB_ID=$(sbatch --parsable --dependency=afterany:$ARRAY_JOB_ID aggregator.sh)

echo "Aggregator Job Submitted with ID: $AGG_JOB_ID"
echo "The aggregator will wait in the queue until the array is finished."