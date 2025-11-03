#!/bin/bash
#SBATCH --job-name=fineweb-data-processing
#SBATCH --output=logs/fineweb_data_%j.out
#SBATCH --error=logs/fineweb_data_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32GB
#SBATCH --time=48:00:00
#SBATCH --partition=compute-queue

# Job information
echo "Starting FineWeb-Data processing job on $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $(hostname)"
echo "Working directory: $(pwd)"

# Load environment
export CONDA_DEFAULT_ENV=datatrove
export CONDA_PREFIX=/shared/conda/envs/datatrove
export PATH=$CONDA_PREFIX/bin:$PATH

# Set environment variables from .env file
if [ -f "/shared/fineweb-data/.env" ]; then
    set -a
    source /shared/fineweb-data/.env
    set +a
    echo "Environment variables loaded from .env"
else
    echo "Warning: .env file not found at /shared/fineweb-data/.env"
fi

# Change to working directory
cd /shared/fineweb-data

# Run the processing script
echo "Running FineWeb-Data processing..."
python finewebdata.py \
    --domain "data law" \
    --mode slurm \
    --cluster-name finewebdata-slurm-cluster \
    --year 2025 \
    --output-bucket fineweb-data \
    --min-words 200 \
    --domain-threshold 2 \
    --compression gzip \
    --non-interactive

echo "FineWeb-Data processing completed on $(date)"
