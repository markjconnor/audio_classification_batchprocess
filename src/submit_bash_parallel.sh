#!/bin/bash
#SBATCH --job-name=bash_parallel
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4          # We ask for 4 CPU cores
#SBATCH --array=0-99               # 100 total array jobs
#SBATCH --output=/beegfs/dataset/logs/chunk_%a.out

BATCH_SIZE=100
MASTER_LIST="/beegfs/dataset/master_list.txt"

# Load the master list into Bash memory
readarray -t files < $MASTER_LIST
num_files=${#files[@]}

# Calculate our specific chunk of 100 files
start_idx=$(( SLURM_ARRAY_TASK_ID * BATCH_SIZE ))
end_idx=$(( start_idx + BATCH_SIZE - 1 ))

# Safety check for the end of the list
if [ $end_idx -ge $num_files ]; then
    end_idx=$(( num_files - 1 ))
fi

echo "Task $SLURM_ARRAY_TASK_ID: Processing files $start_idx to $end_idx"

source /home/almalinux/comp0239_cw/venv/bin/activate

# The Parallel Loop
for (( idx=start_idx; idx<=end_idx; idx++ )); do
    current_file=${files[$idx]}
    
    # Launch Python in the background (&)
    /home/almalinux/comp0239_cw/music-venv/bin/python3 predict_single.py "$current_file" &

    # Once we hit 4 parallel background jobs, wait for them to finish before continuing
    if (( (idx - start_idx + 1) % 4 == 0 )); then
        wait
    fi
done

# Catch any remaining background jobs at the very end
wait
echo "Chunk complete!"