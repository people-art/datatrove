#!/bin/bash

# This script automates the creation and cleanup of a Slurm cluster on AWS using AWS ParallelCluster.
# Adapted for FineWeb-Data processing pipeline
# Usage:
#   ./setup_slurm_cluster.sh [--create|--cleanup|--help]
#   --create  : Create the Slurm cluster (default)
#   --cleanup : Clean up all created resources
#   --help    : Show this help message
#
# Prerequisites:
# - AWS CLI installed and configured with credentials.
# - Sufficient AWS quotas for EC2 instances.
# - SSH key pair created in AWS.
# - Run this script in a directory where you have write permissions.

set -e  # Exit on error

# User-configurable variables
REGION="us-east-1"                # AWS Region
VPC_CIDR="10.0.0.0/16"            # VPC CIDR block
SUBNET_CIDR="10.0.1.0/24"         # Subnet CIDR block
AVAILABILITY_ZONE="${REGION}b"    # Availability Zone
SSH_KEY_NAME="AWS-Keys"        # Your EC2 SSH key pair name
CLUSTER_NAME="finewebdata-slurm-cluster"   # Cluster name for FineWeb-Data
HEAD_INSTANCE_TYPE="t3.medium"    # Head node instance type
COMPUTE_INSTANCE_TYPE="t3.xlarge" # Compute node instance type
MIN_COMPUTE_NODES=1              # Min compute nodes (static)
MAX_COMPUTE_NODES=5              # Max compute nodes (static + dynamic)
CONFIG_FILE="config.yaml"         # Cluster config file name

# Parse command line arguments
ACTION="create"
while [[ $# -gt 0 ]]; do
    case $1 in
        --create)
            ACTION="create"
            shift
            ;;
        --cleanup|--delete)
            ACTION="cleanup"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --create    Create the Slurm cluster (default)"
            echo "  --cleanup   Clean up all created resources"
            echo "  --delete    Alias for --cleanup"
            echo "  --help      Show this help message"
            echo ""
            echo "Prerequisites:"
            echo "  - AWS CLI installed and configured with credentials"
            echo "  - Sufficient AWS quotas for EC2 instances"
            echo "  - SSH key pair created in AWS"
            echo "  - Run this script in a directory where you have write permissions"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to install AWS ParallelCluster
install_parallelcluster() {
    echo "Installing AWS ParallelCluster..."
    pip3 install --user aws-parallelcluster || pip install aws-parallelcluster
    export PATH="$HOME/.local/bin:$PATH"
    pcluster version || { echo "Installation failed"; exit 1; }
    echo "AWS ParallelCluster installed successfully."
}

# Function to cleanup all resources
cleanup_resources() {
    echo "WARNING: This will delete the following resources:"
    echo "  - Slurm cluster: ${CLUSTER_NAME}"
    echo "  - EFS filesystem (if exists)"
    echo "  - VPC and subnets with CIDR: ${VPC_CIDR}"
    echo "  - Internet gateway"
    echo "  - Configuration file: ${CONFIG_FILE}"
    echo ""
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cleanup cancelled."
        exit 0
    fi
    echo "Starting cleanup of all resources..."

    # Step 1: Delete the cluster if it exists
    echo "Step 1: Checking for existing cluster..."
    if pcluster describe-cluster --cluster-name ${CLUSTER_NAME} --region ${REGION} >/dev/null 2>&1; then
        echo "Deleting cluster ${CLUSTER_NAME}..."
        pcluster delete-cluster --cluster-name ${CLUSTER_NAME} --region ${REGION}

        # Wait for cluster deletion
        echo "Waiting for cluster deletion to complete..."
        STATUS="DELETE_IN_PROGRESS"
        MAX_WAIT_TIME=1800  # 30 minutes
        WAIT_TIME=0

        while [ "${STATUS}" == "DELETE_IN_PROGRESS" ] && [ ${WAIT_TIME} -lt ${MAX_WAIT_TIME} ]; do
            sleep 30
            WAIT_TIME=$((WAIT_TIME + 30))
            if pcluster describe-cluster --cluster-name ${CLUSTER_NAME} --region ${REGION} >/dev/null 2>&1; then
                STATUS=$(pcluster describe-cluster --cluster-name ${CLUSTER_NAME} --query "clusterStatus" --output text --region ${REGION})
                echo "Current status: ${STATUS} (waited ${WAIT_TIME}s)"
            else
                STATUS="DELETE_COMPLETE"
            fi
        done

        if [ "${STATUS}" != "DELETE_COMPLETE" ]; then
            echo "Warning: Cluster deletion may not have completed. Status: ${STATUS}"
        else
            echo "Cluster deleted successfully."
        fi
    else
        echo "No cluster found to delete."
    fi

    # Step 2: Delete EFS filesystem if it exists
    echo "Step 2: Checking for EFS filesystem..."
    EFS_ID=$(aws efs describe-file-systems --region ${REGION} --query "FileSystems[?Name=='efs-storage-${CLUSTER_NAME}'].FileSystemId" --output text)
    if [ "${EFS_ID}" != "None" ] && [ -n "${EFS_ID}" ]; then
        echo "Deleting EFS filesystem ${EFS_ID}..."

        # Delete mount targets first
        MOUNT_TARGETS=$(aws efs describe-mount-targets --file-system-id ${EFS_ID} --region ${REGION} --query "MountTargets[].MountTargetId" --output text)
        for MT_ID in ${MOUNT_TARGETS}; do
            echo "Deleting mount target ${MT_ID}..."
            aws efs delete-mount-target --mount-target-id ${MT_ID} --region ${REGION} || echo "Failed to delete mount target ${MT_ID}"
        done

        # Wait for mount targets to be deleted
        sleep 30

        # Delete the filesystem
        aws efs delete-file-system --file-system-id ${EFS_ID} --region ${REGION} || echo "Failed to delete EFS filesystem ${EFS_ID}"
        echo "EFS filesystem deleted."
    else
        echo "No EFS filesystem found to delete."
    fi

    # Step 3: Clean up network resources
    echo "Step 3: Cleaning up network resources..."

    # Find VPC by CIDR or tags
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=cidr-block,Values=${VPC_CIDR}" --query "Vpcs[0].VpcId" --output text --region ${REGION})
    if [ "${VPC_ID}" != "None" ] && [ -n "${VPC_ID}" ]; then
        echo "Found VPC: ${VPC_ID}"

        # Find and delete subnets
        SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=${VPC_ID}" --query "Subnets[].SubnetId" --output text --region ${REGION})
        for SUBNET_ID in ${SUBNET_IDS}; do
            echo "Deleting subnet ${SUBNET_ID}..."
            aws ec2 delete-subnet --subnet-id ${SUBNET_ID} --region ${REGION} || echo "Failed to delete subnet ${SUBNET_ID}"
        done

        # Find and detach/delete internet gateway
        IGW_ID=$(aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=${VPC_ID}" --query "InternetGateways[0].InternetGatewayId" --output text --region ${REGION})
        if [ "${IGW_ID}" != "None" ] && [ -n "${IGW_ID}" ]; then
            echo "Detaching and deleting internet gateway ${IGW_ID}..."
            aws ec2 detach-internet-gateway --vpc-id ${VPC_ID} --internet-gateway-id ${IGW_ID} --region ${REGION} || echo "Failed to detach IGW"
            aws ec2 delete-internet-gateway --internet-gateway-id ${IGW_ID} --region ${REGION} || echo "Failed to delete IGW ${IGW_ID}"
        fi

        # Delete the VPC
        echo "Deleting VPC ${VPC_ID}..."
        aws ec2 delete-vpc --vpc-id ${VPC_ID} --region ${REGION} || echo "Failed to delete VPC ${VPC_ID}"
    else
        echo "No VPC found with CIDR ${VPC_CIDR} to delete."
    fi

    # Clean up config file
    if [ -f "${CONFIG_FILE}" ]; then
        echo "Removing config file ${CONFIG_FILE}..."
        rm -f ${CONFIG_FILE}
    fi

    echo "Cleanup completed!"
}

# Function to create the cluster
create_cluster() {
    # Step 1: Install AWS ParallelCluster
    install_parallelcluster

    # Step 2: Check or Create VPC and Subnet
    echo "Step 2: Setting up VPC and Subnet..."

    # Check if VPC exists (assuming a tag or manual check; for simplicity, create new if not specified)
    VPC_ID=$(aws ec2 describe-vpcs --filters "Name=cidr-block,Values=${VPC_CIDR}" --query "Vpcs[0].VpcId" --output text --region ${REGION})
    if [ "${VPC_ID}" == "None" ]; then
        echo "Creating new VPC..."
        VPC_ID=$(aws ec2 create-vpc --cidr-block ${VPC_CIDR} --query "Vpc.VpcId" --output text --region ${REGION})
        aws ec2 modify-vpc-attribute --vpc-id ${VPC_ID} --enable-dns-hostnames --region ${REGION}
        aws ec2 modify-vpc-attribute --vpc-id ${VPC_ID} --enable-dns-support --region ${REGION}
        echo "VPC created: ${VPC_ID}"
    else
        echo "Using existing VPC: ${VPC_ID}"
    fi

    # Create or get Subnet
    SUBNET_ID=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=${VPC_ID}" "Name=cidr-block,Values=${SUBNET_CIDR}" --query "Subnets[0].SubnetId" --output text --region ${REGION})
    if [ "${SUBNET_ID}" == "None" ]; then
        echo "Creating Subnet..."
        SUBNET_ID=$(aws ec2 create-subnet --vpc-id ${VPC_ID} --cidr-block ${SUBNET_CIDR} --availability-zone ${AVAILABILITY_ZONE} --query "Subnet.SubnetId" --output text --region ${REGION})
        echo "Subnet created: ${SUBNET_ID}"
    else
        echo "Using existing Subnet: ${SUBNET_ID}"
    fi

    # Create Internet Gateway if not exists
    IGW_ID=$(aws ec2 describe-internet-gateways --filters "Name=attachment.vpc-id,Values=${VPC_ID}" --query "InternetGateways[0].InternetGatewayId" --output text --region ${REGION})
    if [ "${IGW_ID}" == "None" ]; then
        echo "Creating Internet Gateway..."
        IGW_ID=$(aws ec2 create-internet-gateway --query "InternetGateway.InternetGatewayId" --output text --region ${REGION})
        aws ec2 attach-internet-gateway --vpc-id ${VPC_ID} --internet-gateway-id ${IGW_ID} --region ${REGION}
    fi

    # Update Route Table
    ROUTE_TABLE_ID=$(aws ec2 describe-route-tables --filters "Name=vpc-id,Values=${VPC_ID}" --query "RouteTables[0].RouteTableId" --output text --region ${REGION})

    # Check if default route already exists, create if not
    if ! aws ec2 describe-route-tables --route-table-ids ${ROUTE_TABLE_ID} --query "RouteTables[0].Routes[?GatewayId=='${IGW_ID}' && DestinationCidrBlock=='0.0.0.0/0']" --output text --region ${REGION} | grep -q .; then
        echo "Adding default route to route table..."
        aws ec2 create-route --route-table-id ${ROUTE_TABLE_ID} --destination-cidr-block 0.0.0.0/0 --gateway-id ${IGW_ID} --region ${REGION} || echo "Route may already exist or creation failed"
    else
        echo "Default route already exists in route table"
    fi

    # Enable auto-assign public IP for subnet
    aws ec2 modify-subnet-attribute --subnet-id ${SUBNET_ID} --map-public-ip-on-launch --region ${REGION}

    # Step 3: Create Cluster Configuration File
    echo "Step 3: Creating cluster config file (${CONFIG_FILE})..."
    cat <<EOF > ${CONFIG_FILE}
Region: ${REGION}
Image:
  Os: alinux2
HeadNode:
  InstanceType: ${HEAD_INSTANCE_TYPE}
  Networking:
    SubnetId: ${SUBNET_ID}
  Ssh:
    KeyName: ${SSH_KEY_NAME}
Scheduling:
  Scheduler: slurm
  SlurmQueues:
    - Name: compute-queue
      ComputeResources:
        - Name: compute
          InstanceType: ${COMPUTE_INSTANCE_TYPE}
          MinCount: ${MIN_COMPUTE_NODES}
          MaxCount: ${MAX_COMPUTE_NODES}
      Networking:
        SubnetIds:
          - ${SUBNET_ID}
# SharedStorage:
#   - MountDir: /shared
#     Name: efs-storage
#     StorageType: Efs
Tags:
  - Key: Project
    Value: fineweb-data
  - Key: Environment
    Value: development
EOF
    echo "Config file created."

    # Step 4: Create the Cluster
    echo "Step 4: Creating the Slurm cluster (${CLUSTER_NAME})..."

    # Check if cluster already exists
    if pcluster describe-cluster --cluster-name ${CLUSTER_NAME} --region ${REGION} >/dev/null 2>&1; then
        echo "Cluster ${CLUSTER_NAME} already exists. Checking status..."
        STATUS=$(pcluster describe-cluster --cluster-name ${CLUSTER_NAME} --query "clusterStatus" --output text --region ${REGION})
        if [ "${STATUS}" == "CREATE_COMPLETE" ]; then
            echo "Cluster is already running."
        else
            echo "Cluster exists but status is: ${STATUS}. Please check manually."
            exit 1
        fi
    else
        pcluster create-cluster --cluster-name ${CLUSTER_NAME} --cluster-configuration ${CONFIG_FILE} --region ${REGION}

        # Wait for cluster to be created (poll status)
        echo "Waiting for cluster creation to complete..."
        STATUS="CREATE_IN_PROGRESS"
        MAX_WAIT_TIME=1800  # 30 minutes
        WAIT_TIME=0

        while [ "${STATUS}" == "CREATE_IN_PROGRESS" ] && [ ${WAIT_TIME} -lt ${MAX_WAIT_TIME} ]; do
            sleep 60
            WAIT_TIME=$((WAIT_TIME + 60))
            STATUS=$(pcluster describe-cluster --cluster-name ${CLUSTER_NAME} --query "clusterStatus" --output text --region ${REGION})
            echo "Current status: ${STATUS} (waited ${WAIT_TIME}s)"
        done

        if [ "${STATUS}" != "CREATE_COMPLETE" ]; then
            echo "Cluster creation failed or timed out. Status: ${STATUS}"
            echo "Check cluster logs with: pcluster get-cluster-log-events --cluster-name ${CLUSTER_NAME} --region ${REGION}"
            exit 1
        fi
        echo "Cluster created successfully."
    fi

    # Step 5: Access and Test the Cluster
    echo "Step 5: Accessing and testing the cluster..."
    # Get head node public IP
    HEAD_NODE_IP=$(pcluster describe-cluster --cluster-name ${CLUSTER_NAME} --query "headNode.publicIpAddress" --output text --region ${REGION})
    echo "Head node IP: ${HEAD_NODE_IP}"

    # SSH into head node (assuming key is in ~/.ssh/; user runs this manually for security)
    echo "To SSH into head node: ssh -i ~/.ssh/${SSH_KEY_NAME} ec2-user@${HEAD_NODE_IP}"
    echo "Note: Your SSH key file may be named '${SSH_KEY_NAME}.pem' or just '${SSH_KEY_NAME}' depending on how you downloaded it from AWS."
    echo "Once inside, test Slurm with: sinfo, squeue, sbatch --wrap 'hostname'"

    echo "Script completed. Cluster is ready."
}

# Main logic based on action
case ${ACTION} in
    "create")
        create_cluster
        ;;
    "cleanup")
        cleanup_resources
        ;;
    *)
        echo "Unknown action: ${ACTION}"
        exit 1
        ;;
esac
