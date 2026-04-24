#!/bin/bash

MASTER_LIST="/beegfs/dataset/master_list.txt"
BATCH_SIZE=100
ITERATIONS=5

# 1. Clean the slate before the 24-hour test begins
echo "Cleaning up old data for a fresh capacity test..."
rm -f /beegfs/almalinux/chunk_*.out
rm -f /beegfs/dataset/results.db

# 2. Calculate Array dimensions
TOTAL_FILES=$(wc -l < "$MASTER_LIST")
TOTAL_CHUNKS=$(( (TOTAL_FILES + BATCH_SIZE - 1) / BATCH_SIZE ))
MAX_INDEX=$(( TOTAL_CHUNKS - 1 ))

echo "========================================="
echo "  INITIATING CAPACITY TEST"
echo "========================================="
echo "- Total Files per run : $TOTAL_FILES"
echo "- Total Iterations    : $ITERATIONS"
echo "- Total Files to process: $(( TOTAL_FILES * ITERATIONS ))"
echo "========================================="

PREV_JOB_ID=""

# 3. Chain the 5 Array Jobs together
for i in $(seq 1 $ITERATIONS); do
    if [ -z "$PREV_JOB_ID" ]; then
        # Iteration 1: No dependency, starts immediately
        PREV_JOB_ID=$(sbatch --parsable --array=0-$MAX_INDEX submit_bash_parallel.sh)
        echo "Iteration $i Queued (Job ID: $PREV_JOB_ID) - Will start immediately."
    else
        # Iterations 2-5: Wait for the previous iteration to finish
        PREV_JOB_ID=$(sbatch --parsable --dependency=afterany:$PREV_JOB_ID --array=0-$MAX_INDEX submit_bash_parallel.sh)
        echo "Iteration $i Queued (Job ID: $PREV_JOB_ID) - Waiting on Iteration $((i-1))."
    fi
done

# 4. Chain the Database Aggregator to the very last iteration
AGG_JOB_ID=$(sbatch --parsable --dependency=afterany:$PREV_JOB_ID aggregator.sh)

echo "========================================="
echo "Capacity Test Fully Queued!"
echo "The Database Aggregator (Job $AGG_JOB_ID) will run after Iteration $ITERATIONS completes."
echo "You can monitor the chain using: squeue"