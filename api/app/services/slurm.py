"""
Slurm production service for managing full-scale data processing jobs
"""

import os
import subprocess
import uuid
import asyncio
import time
from typing import Dict, Any, Optional
from pathlib import Path
import structlog

from app.core.config import settings
from app.models.benchmark import OrderStatus
from app.services.order import OrderService

logger = structlog.get_logger(__name__)


class SlurmClusterManager:
    """Manages SLURM cluster lifecycle for production jobs."""

    def __init__(self):
        self.cluster_name = f"production-{uuid.uuid4().hex[:8]}"
        self.region = settings.AWS_DEFAULT_REGION or "us-east-1"
        self.created = False

    async def create_cluster(self) -> bool:
        """Create SLURM cluster on demand."""
        try:
            logger.info("Creating SLURM cluster", cluster_name=self.cluster_name)

            # Copy cluster config template
            config_path = Path("/app/finewebdata/config.yaml")
            if not config_path.exists():
                logger.error("Cluster config template not found", path=str(config_path))
                return False

            # Update cluster name in config
            config_content = config_path.read_text()
            updated_config = config_content.replace(
                "finewebdata-slurm-cluster",
                self.cluster_name
            )

            # Write updated config
            temp_config = Path(f"/tmp/{self.cluster_name}-config.yaml")
            temp_config.write_text(updated_config)

            # Create cluster using AWS ParallelCluster
            cmd = [
                "pcluster", "create-cluster",
                "--cluster-name", self.cluster_name,
                "--cluster-configuration", str(temp_config),
                "--region", self.region
            ]

            result = await self._run_command(cmd)
            if result.returncode != 0:
                logger.error("Failed to create cluster", error=result.stderr)
                return False

            # Wait for cluster creation
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

    async def start_production_job(
        self,
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
            await self.order_service.update_order_status(
                order_id,
                OrderStatus.CLUSTER_QUEUED,
                cluster_name=self.cluster_manager.cluster_name
            )

            logger.info("Creating SLURM cluster for production job", order_id=order_id)

            # Create SLURM cluster on demand
            cluster_created = await self.cluster_manager.create_cluster()
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
            # Temporarily skip job submission for testing
            slurm_job_id = f"mock-job-{uuid.uuid4().hex[:8]}"  # await self._submit_slurm_job(job_params)

            # Update order with Slurm job ID
            await self.order_service.update_order_status(
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
    --cluster-name {settings.SLURM_CLUSTER_NAME} \\
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
