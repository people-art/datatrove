"""
Slurm production service for managing full-scale data processing jobs
"""

import os
import subprocess
import uuid
import asyncio
import time
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import structlog
import boto3
import yaml

from app.core.config import settings
from app.models.benchmark import OrderStatus
from app.services.order import OrderService

logger = structlog.get_logger(__name__)


class SlurmClusterManager:
    """Manages SLURM cluster lifecycle for production jobs."""

    def __init__(self):
        self.cluster_name = f"production-{uuid.uuid4().hex[:8]}"
        self.region = settings.AWS_DEFAULT_REGION or "us-east-1"
        self.vpc_cidr = "10.0.0.0/16"
        self.subnet_cidr = "10.0.1.0/24"
        self.availability_zone = f"{self.region}b"
        self.created = False

        # AWS clients
        self.ec2 = boto3.client('ec2', region_name=self.region)
        self.efs = boto3.client('efs', region_name=self.region)

    async def _ensure_parallelcluster(self) -> bool:
        """Ensure AWS ParallelCluster is installed."""
        try:
            result = await self._run_command(['pcluster', 'version'])
            if result.returncode == 0:
                logger.info("AWS ParallelCluster already installed")
                return True
        except Exception:
            pass

        logger.info("Installing AWS ParallelCluster...")
        try:
            # Try pip3 first, then pip
            result = await self._run_command([
                'pip3', 'install', '--user', 'aws-parallelcluster'
            ])
            if result.returncode != 0:
                result = await self._run_command([
                    'pip', 'install', 'aws-parallelcluster'
                ])

            if result.returncode == 0:
                logger.info("AWS ParallelCluster installed successfully")
                return True
            else:
                logger.error("Failed to install AWS ParallelCluster", error=result.stderr)
                return False
        except Exception as e:
            logger.error("ParallelCluster installation failed", error=str(e))
            return False

    async def _ensure_vpc_and_subnet(self) -> Tuple[str, str]:
        """Ensure VPC and subnet exist, return (vpc_id, subnet_id)."""
        # Check for existing VPC
        vpc_response = self.ec2.describe_vpcs(
            Filters=[{'Name': 'cidr-block', 'Values': [self.vpc_cidr]}]
        )

        if vpc_response['Vpcs']:
            vpc_id = vpc_response['Vpcs'][0]['VpcId']
            logger.info("Using existing VPC", vpc_id=vpc_id)
        else:
            # Create new VPC
            vpc_response = self.ec2.create_vpc(CidrBlock=self.vpc_cidr)
            vpc_id = vpc_response['Vpc']['VpcId']

            # Enable DNS hostnames and support
            self.ec2.modify_vpc_attribute(
                VpcId=vpc_id,
                EnableDnsHostnames={'Value': True}
            )
            self.ec2.modify_vpc_attribute(
                VpcId=vpc_id,
                EnableDnsSupport={'Value': True}
            )
            logger.info("Created new VPC", vpc_id=vpc_id)

        # Check for existing subnet
        subnet_response = self.ec2.describe_subnets(
            Filters=[
                {'Name': 'vpc-id', 'Values': [vpc_id]},
                {'Name': 'cidr-block', 'Values': [self.subnet_cidr]}
            ]
        )

        if subnet_response['Subnets']:
            subnet_id = subnet_response['Subnets'][0]['SubnetId']
            logger.info("Using existing subnet", subnet_id=subnet_id)
        else:
            # Create new subnet
            subnet_response = self.ec2.create_subnet(
                VpcId=vpc_id,
                CidrBlock=self.subnet_cidr,
                AvailabilityZone=self.availability_zone
            )
            subnet_id = subnet_response['Subnet']['SubnetId']

            # Enable auto-assign public IP
            self.ec2.modify_subnet_attribute(
                SubnetId=subnet_id,
                MapPublicIpOnLaunch={'Value': True}
            )
            logger.info("Created new subnet", subnet_id=subnet_id)

        return vpc_id, subnet_id

    async def _ensure_internet_gateway_and_routes(self, vpc_id: str, subnet_id: str):
        """Ensure internet gateway and routing are configured."""
        # Check for existing IGW
        igw_response = self.ec2.describe_internet_gateways(
            Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}]
        )

        if igw_response['InternetGateways']:
            igw_id = igw_response['InternetGateways'][0]['InternetGatewayId']
            logger.info("Using existing IGW", igw_id=igw_id)
        else:
            # Create and attach IGW
            igw_response = self.ec2.create_internet_gateway()
            igw_id = igw_response['InternetGateway']['InternetGatewayId']

            self.ec2.attach_internet_gateway(
                VpcId=vpc_id,
                InternetGatewayId=igw_id
            )
            logger.info("Created and attached IGW", igw_id=igw_id)

        # Configure route table
        route_table_response = self.ec2.describe_route_tables(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
        )
        route_table_id = route_table_response['RouteTables'][0]['RouteTableId']

        # Check if default route exists
        existing_routes = route_table_response['RouteTables'][0]['Routes']
        has_default_route = any(
            route.get('GatewayId') == igw_id and
            route.get('DestinationCidrBlock') == '0.0.0.0/0'
            for route in existing_routes
        )

        if not has_default_route:
            self.ec2.create_route(
                RouteTableId=route_table_id,
                DestinationCidrBlock='0.0.0.0/0',
                GatewayId=igw_id
            )
            logger.info("Added default route to route table")

    async def _generate_cluster_config(self, subnet_id: str) -> str:
        """Generate cluster configuration file, return path."""
        config = {
            'Region': self.region,
            'ClusterName': self.cluster_name,
            'Image': {'Os': 'alinux2'},
            'HeadNode': {
                'InstanceType': 't3.medium',
                'Networking': {'SubnetId': subnet_id},
                'Ssh': {'KeyName': 'AWS-Keys'}
            },
            'Scheduling': {
                'Scheduler': 'slurm',
                'SlurmQueues': [{
                    'Name': 'compute-queue',
                    'ComputeResources': [{
                        'Name': 'compute',
                        'InstanceType': 't3.xlarge',
                        'MinCount': 1,
                        'MaxCount': settings.SLURM_NUM_NODES
                    }],
                    'Networking': {'SubnetIds': [subnet_id]}
                }]
            },
            'Tags': [
                {'Key': 'Project', 'Value': 'fineweb-data'},
                {'Key': 'Environment', 'Value': 'production'},
                {'Key': 'ClusterName', 'Value': self.cluster_name}
            ]
        }

        config_path = f"/tmp/{self.cluster_name}-config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

        logger.info("Generated cluster config", config_path=config_path)
        return config_path

    async def _cluster_exists(self) -> bool:
        """Check if cluster already exists."""
        try:
            cmd = [
                "pcluster", "describe-cluster",
                "--cluster-name", self.cluster_name,
                "--region", self.region,
                "--query", "clusterStatus",
                "--output", "text"
            ]
            result = await self._run_command(cmd)
            return result.returncode == 0
        except Exception:
            return False

    async def _cluster_ready(self) -> bool:
        """Check if cluster is in CREATE_COMPLETE status."""
        try:
            cmd = [
                "pcluster", "describe-cluster",
                "--cluster-name", self.cluster_name,
                "--region", self.region,
                "--query", "clusterStatus",
                "--output", "text"
            ]
            result = await self._run_command(cmd)
            status = result.stdout.strip()
            return status == "CREATE_COMPLETE"
        except Exception:
            return False

    async def create_cluster(self) -> bool:
        """Create SLURM cluster on demand with full infrastructure."""
        try:
            logger.info("Creating SLURM cluster", cluster_name=self.cluster_name)

            # 1. Ensure AWS ParallelCluster is installed
            if not await self._ensure_parallelcluster():
                return False

            # 2. Ensure VPC and subnet exist
            vpc_id, subnet_id = await self._ensure_vpc_and_subnet()

            # 3. Ensure internet gateway and routes
            await self._ensure_internet_gateway_and_routes(vpc_id, subnet_id)

            # 4. Generate cluster configuration
            config_path = await self._generate_cluster_config(subnet_id)

            # 5. Check if cluster already exists
            if await self._cluster_exists():
                if await self._cluster_ready():
                    logger.info("Cluster already exists and ready")
                    self.created = True
                    return True
                else:
                    logger.warning("Cluster exists but not in ready state")
                    return False

            # 6. Create cluster using AWS ParallelCluster
            cmd = [
                "pcluster", "create-cluster",
                "--cluster-name", self.cluster_name,
                "--cluster-configuration", config_path,
                "--region", self.region
            ]

            result = await self._run_command(cmd)
            if result.returncode != 0:
                logger.error("Failed to create cluster", error=result.stderr)
                return False

            # 7. Wait for cluster creation to complete
            if await self._wait_for_cluster_ready():
                self.created = True
                logger.info("SLURM cluster created successfully", cluster_name=self.cluster_name)
                return True
            else:
                logger.error("Cluster creation timed out")
                return False

        except Exception as e:
            logger.error("Cluster creation failed", error=str(e))
            return False

    def delete_cluster_sync(self) -> bool:
        """Delete SLURM cluster (synchronous version)."""
        import asyncio
        return asyncio.run(self.delete_cluster())

    async def delete_cluster(self) -> bool:
        """Delete SLURM cluster."""
        if not self.created:
            logger.info("Cluster not created, skipping deletion")
            return True

        try:
            logger.info("Deleting SLURM cluster", cluster_name=self.cluster_name)

            cmd = [
                "pcluster", "delete-cluster",
                "--cluster-name", self.cluster_name,
                "--region", self.region
            ]

            result = await self._run_command(cmd)
            if result.returncode != 0:
                logger.error("Failed to delete cluster", error=result.stderr)
                return False

            # Wait for cluster deletion
            if await self._wait_for_cluster_deleted():
                logger.info("SLURM cluster deleted successfully", cluster_name=self.cluster_name)
                return True
            else:
                logger.warning("Cluster deletion may not have completed")
                return False

        except Exception as e:
            logger.error("Cluster deletion failed", error=str(e))
            return False

    async def _wait_for_cluster_ready(self, timeout: int = 1800) -> bool:
        """Wait for cluster to be ready."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                cmd = [
                    "pcluster", "describe-cluster",
                    "--cluster-name", self.cluster_name,
                    "--region", self.region,
                    "--query", "clusterStatus",
                    "--output", "text"
                ]

                result = await self._run_command(cmd)
                if result.returncode == 0 and result.stdout.strip() == "CREATE_COMPLETE":
                    return True

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.warning("Failed to check cluster status", error=str(e))
                await asyncio.sleep(30)

        return False

    async def _wait_for_cluster_deleted(self, timeout: int = 900) -> bool:
        """Wait for cluster to be deleted."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                cmd = [
                    "pcluster", "describe-cluster",
                    "--cluster-name", self.cluster_name,
                    "--region", self.region,
                    "--query", "clusterStatus",
                    "--output", "text"
                ]

                result = await self._run_command(cmd)
                if result.returncode != 0:  # Cluster doesn't exist anymore
                    return True

                status = result.stdout.strip()
                if status == "DELETE_COMPLETE":
                    return True

                await asyncio.sleep(30)

            except Exception as e:
                logger.warning("Failed to check cluster deletion status", error=str(e))
                await asyncio.sleep(30)

        return False

    async def _run_command(self, cmd: list) -> subprocess.CompletedProcess:
        """Run shell command asynchronously."""
        cmd_str = ' '.join(cmd)
        process = await asyncio.create_subprocess_shell(
            cmd_str,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/app"
        )

        stdout, stderr = await process.communicate()
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout=stdout.decode(),
            stderr=stderr.decode()
        )


class SlurmProductionService:
    """Service for managing Slurm-based production data processing jobs."""

    def __init__(self, order_service: OrderService):
        self.order_service = order_service
        self.cluster_manager = None  # Will be initialized per job

    def start_production_job_sync(
        self,
        db_session,
        order_id: str,
        benchmark_job_id: str,
        domain: str,
        keywords: list,
        languages: list,
        time_range_start: str,
        time_range_end: str,
        quality_tier: str,
    ) -> str:
        """Start a full production data processing job on Slurm cluster."""

        # Initialize cluster manager for this job
        self.cluster_manager = SlurmClusterManager()

        try:
            # Update order status to cluster queued
            self.order_service.update_order_status_sync(
                db_session,
                order_id,
                OrderStatus.CLUSTER_QUEUED,
                cluster_name=self.cluster_manager.cluster_name
            )

            logger.info("Creating SLURM cluster for production job", order_id=order_id)

            # Create SLURM cluster on demand (this is still async, need to run in sync context)
            import asyncio
            cluster_created = asyncio.run(self.cluster_manager.create_cluster())
            if not cluster_created:
                raise Exception("Failed to create SLURM cluster")

            # Generate unique job identifier
            job_suffix = str(uuid.uuid4())[:8]
            domain_slug = domain.replace(' ', '-').replace('_', '-').lower()
            job_name = f"finedata-{domain_slug}-{job_suffix}"

            # Prepare job parameters
            job_params = {
                'job_name': job_name,
                'domain': domain,
                'keywords': keywords,
                'languages': languages,
                'time_range_start': time_range_start,
                'time_range_end': time_range_end,
                'quality_tier': quality_tier,
                'order_id': order_id,
                'benchmark_job_id': benchmark_job_id,
                'cluster_name': self.cluster_manager.cluster_name,
            }

            # Submit Slurm job
            slurm_job_id = asyncio.run(self._submit_slurm_job(job_params))

            # Update order with Slurm job ID
            self.order_service.update_order_status_sync(
                db_session,
                order_id,
                OrderStatus.RUNNING,
                slurm_job_id=slurm_job_id,
                cluster_name=self.cluster_manager.cluster_name
            )

            logger.info(
                "Production job submitted to Slurm",
                order_id=order_id,
                slurm_job_id=slurm_job_id,
                job_name=job_name,
                cluster_name=self.cluster_manager.cluster_name
            )

            return slurm_job_id

        except Exception as e:
            logger.error(
                "Failed to start production job",
                order_id=order_id,
                error=str(e)
            )

            # Cleanup cluster if it was created
            if self.cluster_manager and self.cluster_manager.created:
                await self.cluster_manager.delete_cluster()

            # Update order status to failed
            await self.order_service.update_order_status(
                order_id,
                OrderStatus.FAILED,
                error_message=f"Failed to start production job: {str(e)}"
            )

            raise

    async def _submit_slurm_job(self, job_params: Dict[str, Any]) -> str:
        """Submit job to Slurm cluster using sbatch."""

        # Create job script
        script_path = await self._create_slurm_script(job_params)

        try:
            # Submit job using sbatch
            cmd = ['sbatch', str(script_path)]
            result = await self._run_command(cmd)

            # Parse job ID from sbatch output
            # Output format: "Submitted batch job <job_id>"
            output_lines = result.stdout.strip().split('\n')
            last_line = output_lines[-1]

            if "Submitted batch job" in last_line:
                job_id = last_line.split()[-1]
                return job_id
            else:
                raise Exception(f"Unexpected sbatch output: {last_line}")

        except Exception as e:
            logger.error("Slurm job submission failed", error=str(e))
            raise

    async def _create_slurm_script(self, job_params: Dict[str, Any]) -> Path:
        """Create Slurm job script for data processing."""

        script_dir = Path("/tmp/finedata-jobs")
        script_dir.mkdir(exist_ok=True)

        script_path = script_dir / f"{job_params['job_name']}.sh"

        # Generate keywords string for command line
        keywords_str = ','.join(job_params['keywords'])
        languages_str = ','.join(job_params['languages'])

        # Create Slurm script content
        script_content = f"""#!/bin/bash
#SBATCH --job-name={job_params['job_name']}
#SBATCH --output=/home/ubuntu/datatrove/logs/production/%j.out
#SBATCH --error=/home/ubuntu/datatrove/logs/production/%j.err
#SBATCH --time=48:00:00
#SBATCH --nodes={settings.SLURM_NUM_NODES}
#SBATCH --ntasks-per-node=1
#SBATCH --mem=32GB
#SBATCH --cpus-per-task=4
#SBATCH --partition=hopper-cpu
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user={settings.EMAIL_FROM}

# Load environment and activate conda
export PYTHONPATH=/home/ubuntu/datatrove/src:$PYTHONPATH
cd /home/ubuntu/datatrove

# Set environment variables for the job
export FINEDATA_ORDER_ID={job_params['order_id']}
export FINEDATA_JOB_ID={job_params['benchmark_job_id']}

# Run FineWeb-Data production processing
python finewebdata/finewebdata.py \\
    --domain "{job_params['domain']}" \\
    --mode slurm \\
    --keywords "{keywords_str}" \\
    --languages "{languages_str}" \\
    --time-range-start {job_params['time_range_start']} \\
    --time-range-end {job_params['time_range_end']} \\
    --quality-tier {job_params['quality_tier']} \\
    --output-bucket finedata-production \\
    --cluster-name {job_params['cluster_name']} \\
    --use-llm-scoring \\
    --gpu

# Check if processing succeeded
if [ $? -eq 0 ]; then
    echo "Production processing completed successfully"

    # Trigger delivery workflow
    python -c "
import asyncio
import sys
sys.path.append('/home/ubuntu/datatrove/api')
from app.services.delivery import DeliveryService
from app.db.session import async_session_factory

async def deliver():
    async with async_session_factory() as db:
        delivery_service = DeliveryService()
        await delivery_service.deliver_dataset('{job_params['order_id']}', db)

asyncio.run(deliver())
"

    # Cleanup SLURM cluster after successful delivery
    echo "Cleaning up SLURM cluster: {job_params['cluster_name']}"
    pcluster delete-cluster --cluster-name {job_params['cluster_name']} --region us-east-1

    # Wait for cluster deletion (optional, job will complete regardless)
    echo "Waiting for cluster cleanup..."
    sleep 60

else
    echo "Production processing failed"
    # Still cleanup cluster even on failure
    echo "Cleaning up SLURM cluster due to failure: {job_params['cluster_name']}"
    pcluster delete-cluster --cluster-name {job_params['cluster_name']} --region us-east-1 || echo "Cluster cleanup failed"
    exit 1
fi
"""

        # Write script to file
        with open(script_path, 'w') as f:
            f.write(script_content)

        # Make script executable
        script_path.chmod(0o755)

        logger.info("Slurm script created", script_path=str(script_path))
        return script_path

    def check_job_status_sync(self, slurm_job_id: str) -> Dict[str, Any]:
        """Check the status of a Slurm job (synchronous version)."""
        import asyncio
        return asyncio.run(self.check_job_status(slurm_job_id))

    async def check_job_status(self, slurm_job_id: str) -> Dict[str, Any]:
        """Check the status of a Slurm job."""

        try:
            cmd = ['squeue', '--job', slurm_job_id, '--format=%i,%T,%R,%N']
            result = await self._run_command(cmd)

            if result.returncode == 0 and result.stdout.strip():
                # Parse job status
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:  # Skip header
                    job_info = lines[1].split(',')
                    return {
                        'job_id': job_info[0],
                        'status': job_info[1],
                        'reason': job_info[2] if len(job_info) > 2 else None,
                        'nodes': job_info[3] if len(job_info) > 3 else None,
                    }

            # Job might be completed, check sacct
            cmd = ['sacct', '--job', slurm_job_id, '--format=JobID,State,ExitCode', '--parsable2']
            result = await self._run_command(cmd)

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    job_info = lines[1].split('|')
                    return {
                        'job_id': job_info[0],
                        'status': job_info[1],
                        'exit_code': job_info[2] if len(job_info) > 2 else None,
                    }

            return {'status': 'UNKNOWN'}

        except Exception as e:
            logger.error("Failed to check job status", slurm_job_id=slurm_job_id, error=str(e))
            return {'status': 'ERROR', 'error': str(e)}

    async def _run_command(self, cmd: list) -> subprocess.CompletedProcess:
        """Run a shell command asynchronously."""

        # Convert to string for subprocess
        cmd_str = ' '.join(cmd)

        # Run command
        process = await asyncio.create_subprocess_shell(
            cmd_str,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/home/ubuntu/datatrove"
        )

        stdout, stderr = await process.communicate()

        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout=stdout.decode(),
            stderr=stderr.decode()
        )
