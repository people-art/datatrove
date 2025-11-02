#!/bin/bash
#SBATCH --job-name=fineweb-med-processing
#SBATCH --output=logs/fineweb_med_%j.out
#SBATCH --error=logs/fineweb_med_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16GB
#SBATCH --time=24:00:00
#SBATCH --partition=compute-queue

# Job information
echo "Starting FineWeb-Med processing job on $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $(hostname)"
echo "Working directory: $(pwd)"

# Load environment
export CONDA_DEFAULT_ENV=datatrove
export CONDA_PREFIX=/shared/conda/envs/datatrove
export PATH=$CONDA_PREFIX/bin:$PATH

# Set environment variables from .env file
if [ -f "/shared/fineweb-med/.env" ]; then
    set -a
    source /shared/fineweb-med/.env
    set +a
    echo "Environment variables loaded from .env"
else
    echo "Warning: .env file not found at /shared/fineweb-med/.env"
fi

# Change to working directory
cd /shared/fineweb-med

# Run the processing script
echo "Running FineWeb-Med processing..."
python fineweb-med-new.py \
    --mode slurm \
    --cluster-name fineweb-med-slurm-cluster \
    --year 2024 \
    --output-bucket fineweb-med \
    --min-words 200 \
    --medical-threshold 3 \
    --compression gzip \
    --non-interactive

echo "FineWeb-Med processing completed on $(date)"
