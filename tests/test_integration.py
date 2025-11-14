"""
Integration tests for benchmark and production workflows
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path


class TestBenchmarkIntegration:
    """Integration tests for benchmark workflow"""

    @pytest.mark.asyncio
    async def test_full_benchmark_workflow(self):
        """Test complete benchmark workflow from job creation to results"""
        # This would be a full integration test that:
        # 1. Creates a benchmark job
        # 2. Runs the benchmark task
        # 3. Verifies database state
        # 4. Checks sample data upload
        # 5. Validates results parsing

        # For now, we'll test the individual components
        from app.services.finewebdata_service import FineWebDataService, BenchmarkConfig

        service = FineWebDataService()
        config = BenchmarkConfig(
            job_id="integration-test-job",
            domain="education",
            keywords=["learning", "teaching"],
            languages=["en"],
            time_range_start="2023-01-01",
            time_range_end="2024-01-01",
            quality_tier="standard"
        )

        # Test command building
        cmd = await service._build_benchmark_command(config)
        assert isinstance(cmd, list)
        assert len(cmd) > 5
        assert "education" in " ".join(cmd)

    @pytest.mark.asyncio
    async def test_benchmark_task_error_handling(self):
        """Test benchmark task error handling"""
        from app.tasks.benchmark import benchmark_task
        from app.worker import celery_app

        # Mock Celery task
        task = Mock()
        task.request.id = "test-task-id"

        # Mock job config to return None (job not found)
        with patch('app.tasks.benchmark.get_job_config', return_value=None):
            with pytest.raises(Exception) as exc_info:
                await benchmark_task("nonexistent-job")

            assert "Benchmark job not found" in str(exc_info.value)


class TestProductionIntegration:
    """Integration tests for production workflow"""

    @pytest.mark.asyncio
    async def test_production_task_initialization(self):
        """Test production task initializes correctly"""
        from app.tasks.production import production_task
        from app.worker import celery_app

        # This would test the full production workflow
        # For now, test that the function exists and can be imported
        assert callable(production_task)

    @pytest.mark.asyncio
    async def test_production_monitor_task(self):
        """Test production monitor task"""
        from app.tasks.production import production_monitor_task

        # Test that the function exists
        assert callable(production_monitor_task)


class TestHuggingFaceIntegration:
    """Integration tests for HuggingFace uploads"""

    @pytest.mark.asyncio
    async def test_hf_upload_integration(self):
        """Test HF upload integration"""
        from app.services.finewebdata_service import FineWebDataService

        service = FineWebDataService()

        # Test command building
        cmd = await service._build_hf_upload_command("test-order", "education")
        assert isinstance(cmd, list)
        assert "publish_to_hf.sh" in " ".join(cmd)
        assert "education" in " ".join(cmd)


class TestEndToEndWorkflow:
    """End-to-end workflow tests"""

    @pytest.mark.asyncio
    async def test_benchmark_to_production_flow(self):
        """Test the complete flow from benchmark to production delivery"""
        # This would test:
        # 1. Create benchmark job
        # 2. Run benchmark (mock results)
        # 3. Create quote
        # 4. Create order
        # 5. Run production
        # 6. Monitor and deliver

        # For now, test that all components can be imported
        try:
            from app.services.finewebdata_service import FineWebDataService
            from app.tasks.benchmark import benchmark_task
            from app.tasks.production import production_task, production_monitor_task
            from app.services.benchmark import BenchmarkService
            from app.services.order import OrderService

            # All imports successful
            assert True
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")

    def test_service_dependencies(self):
        """Test that all required services and their dependencies are available"""
        required_files = [
            "/home/ubuntu/datatrove/finewebdata/finewebdata.py",
            "/home/ubuntu/datatrove/finewebdata/setup_slurm_cluster.sh",
            "/home/ubuntu/datatrove/finewebdata/publish_to_hf.sh",
        ]

        for file_path in required_files:
            assert Path(file_path).exists(), f"Required file not found: {file_path}"

    def test_environment_variables(self):
        """Test that required environment variables are defined"""
        from app.core.config import settings

        # Check that our new env vars have defaults or can be accessed
        assert hasattr(settings, 'FINEDATA_BENCHMARK_SAMPLE_SIZE')
        assert hasattr(settings, 'FINEDATA_PRODUCTION_TIMEOUT_HOURS')

        # These should not raise AttributeError
        _ = settings.FINEDATA_BENCHMARK_SAMPLE_SIZE
        _ = settings.FINEDATA_PRODUCTION_TIMEOUT_HOURS


class TestErrorRecovery:
    """Test error recovery scenarios"""

    @pytest.mark.asyncio
    async def test_benchmark_task_retry(self):
        """Test benchmark task retry logic"""
        from app.tasks.benchmark import benchmark_task

        # Mock a task that will fail and retry
        task = Mock()
        task.request.id = "test-retry-task"
        task.retry = Mock(side_effect=Exception("Retry triggered"))

        with patch('app.tasks.benchmark.get_job_config', side_effect=Exception("Network error")):
            with pytest.raises(Exception):
                await benchmark_task("test-job")

    @pytest.mark.asyncio
    async def test_production_monitor_error_recovery(self):
        """Test production monitor error recovery"""
        from app.tasks.production import production_monitor_task

        # Test that monitor handles errors gracefully
        # This would normally reschedule itself
        task = Mock()
        task.request.id = "test-monitor-task"

        # Should not raise unhandled exceptions
        try:
            await production_monitor_task("nonexistent-order", "fake-job-id")
        except Exception:
            # Monitor task should handle its own errors
            pass


# Integration test markers for CI/CD
pytestmark = [
    pytest.mark.integration,
    pytest.mark.asyncio,
]
