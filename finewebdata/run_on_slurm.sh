#!/bin/bash

# Script to run FineWeb-Data processing on AWS ParallelCluster Slurm
# Adapted for universal domain-specific dataset processing

set -e

CLUSTER_NAME="finewebdata-slurm-cluster"
REGION="us-east-1"

echo "🚀 Starting FineWeb-Data processing on AWS ParallelCluster Slurm"
echo "📊 Cluster: $CLUSTER_NAME"
echo "🌍 Region: $REGION"
echo ""

# Check cluster status
echo "📋 Checking cluster status..."
CLUSTER_STATUS=$(pcluster describe-cluster --cluster-name $CLUSTER_NAME --region $REGION 2>/dev/null | grep -o '"clusterStatus": "[^"]*"' | cut -d'"' -f4 || echo "NOT_FOUND")

if [ "$CLUSTER_STATUS" != "CREATE_COMPLETE" ]; then
    echo "❌ Cluster $CLUSTER_NAME is not ready. Status: $CLUSTER_STATUS"
    echo "💡 Please run: ./setup_slurm_cluster.sh --create"
    exit 1
fi

echo "✅ Cluster is ready!"

# Get head node IP
HEAD_NODE_IP=$(pcluster describe-cluster --cluster-name $CLUSTER_NAME --region $REGION --query "headNode.publicIpAddress" --output text)

if [ -z "$HEAD_NODE_IP" ] || [ "$HEAD_NODE_IP" = "None" ]; then
    echo "❌ Could not get head node IP"
    exit 1
fi

echo "🔗 Head node IP: $HEAD_NODE_IP"

# Copy files to cluster
echo ""
echo "📤 Copying files to cluster..."

# Create directory on cluster
ssh -o StrictHostKeyChecking=no -i ~/.ssh/AWS-Keys ec2-user@$HEAD_NODE_IP "mkdir -p /shared/fineweb-data"

# Copy necessary files
scp -o StrictHostKeyChecking=no -i ~/.ssh/AWS-Keys finewebdata.py ec2-user@$HEAD_NODE_IP:/shared/fineweb-data/
scp -o StrictHostKeyChecking=no -i ~/.ssh/AWS-Keys slurm_job.sh ec2-user@$HEAD_NODE_IP:/shared/fineweb-data/
scp -o StrictHostKeyChecking=no -i ~/.ssh/AWS-Keys ../.env ec2-user@$HEAD_NODE_IP:/shared/fineweb-data/

echo "✅ Files copied to cluster"

# Submit job
echo ""
echo "🎯 Submitting Slurm job..."
JOB_ID=$(ssh -o StrictHostKeyChecking=no -i ~/.ssh/AWS-Keys ec2-user@$HEAD_NODE_IP "cd /shared/fineweb-data && sbatch slurm_job.sh")

echo "✅ Job submitted! Job ID: $JOB_ID"

# Monitor job
echo ""
echo "📊 Monitoring job status..."
echo "💡 You can also monitor manually:"
echo "   ssh -i ~/.ssh/AWS-Keys ec2-user@$HEAD_NODE_IP"
echo "   squeue  # Check job queue"
echo "   tail -f /shared/fineweb-data/logs/fineweb_data_*.out  # View logs"

# Wait a bit and show initial status
sleep 5
ssh -o StrictHostKeyChecking=no -i ~/.ssh/AWS-Keys ec2-user@$HEAD_NODE_IP "squeue" 2>/dev/null || echo "Could not check job status"

echo ""
echo "🎉 Setup complete! The FineWeb-Data processing job is now running on the cluster."
echo "📈 Expected runtime: 24-48 hours for full processing pipeline"
echo "💰 Estimated cost: $100-300 depending on actual usage and domain size"
