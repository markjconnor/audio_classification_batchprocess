#!/bin/bash
#SBATCH --job-name=db_aggregate
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1          # SQLite is single-threaded, 1 CPU is plenty
#SBATCH --output=/beegfs/almalinux/aggregate.log

echo "Starting database aggregation..."
source /home/almalinux/music-venv/bin/activate

# Run the python script we created earlier
/home/almalinux/music-venv/bin/python3 /beegfs/almalinux/aggregate_results.py

echo "Aggregation complete!"