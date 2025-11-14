"""
Unit tests for FineWebData service
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from app.services.finewebdata_service import (
    FineWebDataService,
    BenchmarkConfig,
    ProductionConfig,
    BenchmarkResult,
    ProductionResult
)


class TestFineWebDataService:
    """Test cases for FineWebDataService"""

    @pytest.fixture
    def service(self):
        """Create service instance for testing"""
        return FineWebDataService()

    @pytest.fixture
    def benchmark_config(self):
        """Create benchmark config for testing"""
        return BenchmarkConfig(
            job_id="test-job-123",
            domain="education",
            keywords=["learning", "teaching", "education"],
            languages=["en", "es"],
            time_range_start="2023-01-01",
            time_range_end="2024-01-01",
            quality_tier="standard",
            estimated_scale="1000000"
        )

    @pytest.fixture
    def production_config(self):
        """Create production config for testing"""
        return ProductionConfig(
            order_id="test-order-456",
            benchmark_job_id="test-job-123",
            domain="education",
            keywords=["learning", "teaching", "education"],
            languages=["en", "es"],
            time_range_start="2023-01-01",
            time_range_end="2024-01-01",
            quality_tier="standard"
        )

    def test_service_initialization(self, service):
        """Test service initializes correctly"""
        assert service.project_root == Path("/home/ubuntu/datatrove")
        assert service.finewebdata_script.exists()

    @pytest.mark.asyncio
    async def test_build_benchmark_command(self, service, benchmark_config):
        """Test benchmark command building"""
        cmd = await service._build_benchmark_command(benchmark_config)

        assert "python" in cmd
        assert "finewebdata.py" in " ".join(cmd)
        assert "--domain" in cmd
        assert benchmark_config.domain in cmd
        assert "--keywords" in cmd
        assert "--mode" in cmd
        assert "local" in cmd
        assert "--benchmark" in cmd
        assert "--non-interactive" in cmd

    @pytest.mark.asyncio
    async def test_build_production_command(self, service, production_config):
        """Test production command building"""
        cmd = await service._build_production_command(production_config)

        assert "python" in cmd
        assert "finewebdata.py" in " ".join(cmd)
        assert "--domain" in cmd
        assert production_config.domain in cmd
        assert "--mode" in cmd
        assert "slurm" in cmd
        assert "--use-llm-scoring" in cmd
        assert "--gpu" in cmd
        assert "--non-interactive" in cmd

    @pytest.mark.asyncio
    async def test_build_hf_upload_command(self, service):
        """Test HuggingFace upload command building"""
        cmd = await service._build_hf_upload_command("test-order", "education")

        assert "bash" in cmd
        assert "publish_to_hf.sh" in " ".join(cmd)
        assert "--domain" in cmd
        assert "education" in cmd
        assert "--latest" in cmd

    @pytest.mark.asyncio
    async def test_parse_benchmark_results_success(self, service):
        """Test successful benchmark results parsing"""
        pipeline_output = {
            "stats": {
                "total_docs_processed": 1000000,
                "docs_after_filtering": 850000,
                "docs_after_deduplication": 800000,
                "total_tokens": 80000000
            },
            "quality_metrics": {
                "domain_coverage": 0.85,
                "quality_filter_pass_rate": 0.92,
                "pii_detection_rate": 0.02,
                "toxicity_detection_rate": 0.01,
                "language_distribution": {"en": 637500, "es": 127500},
                "domain_distribution": {"technology": 340000, "science": 212500}
            },
            "sample_s3_url": "https://s3.amazonaws.com/samples/sample.jsonl.gz"
        }

        result = await service._parse_benchmark_results(pipeline_output, "test-job")

        # BenchmarkResult is a dataclass, check attributes
        assert result.docs_read == 1000000
        assert result.docs_kept == 800000
        assert result.tokens == 80000000
        assert result.coverage == 0.85
        assert result.quality_pass_rate == 0.92
        assert result.sample_url == "https://s3.amazonaws.com/samples/sample.jsonl.gz"
        assert hasattr(result, "suggested_params")

    @pytest.mark.asyncio
    async def test_parse_benchmark_results_fallback(self, service):
        """Test benchmark results parsing fallback"""
        # Empty pipeline output should return fallback values
        result = await service._parse_benchmark_results({}, "test-job")

        # BenchmarkResult fallback values
        assert result.docs_read == 1000000  # Fallback value
        assert result.docs_kept == 850000   # Fallback value
        assert result.tokens == 85000000    # Fallback value
        assert "sample_url" in result.sample_url
        assert hasattr(result, "suggested_params")

    def test_generate_suggested_params(self):
        """Test suggested parameters generation via benchmark service"""
        from app.services.benchmark import BenchmarkService

        service = BenchmarkService(None)  # DB not needed for this method
        quality_metrics = {
            "domain_coverage": 0.75,
            "quality_filter_pass_rate": 0.80,
            "pii_detection_rate": 0.03
        }

        params = service._generate_suggested_params(quality_metrics)

        assert "thresholds" in params
        assert "filters" in params
        assert params["thresholds"]["domain"] == 3  # Default
        assert params["filters"]["min_words"] == 100

    @pytest.mark.asyncio
    async def test_run_command_success(self, service):
        """Test successful command execution"""
        cmd = ["echo", "test"]
        result = await service._run_command(cmd)

        assert result.returncode == 0
        assert "test" in result.stdout

    @pytest.mark.asyncio
    async def test_run_command_failure(self, service):
        """Test failed command execution"""
        cmd = ["false"]  # Command that always fails
        result = await service._run_command(cmd)

        assert result.returncode != 0

    @pytest.mark.asyncio
    async def test_upload_to_huggingface_via_delivery_service(self, service):
        """Test HF upload via delivery service"""
        with patch('app.db.session.async_session_factory') as mock_session_factory:
            # Mock the session factory
            mock_session = AsyncMock()
            mock_session_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)

            # Mock delivery service
            with patch('app.services.delivery.DeliveryService') as mock_delivery_class:
                mock_delivery = AsyncMock()
                mock_delivery_class.return_value = mock_delivery
                mock_delivery.deliver_dataset = AsyncMock()

                # Mock order service
                with patch('app.services.order.OrderService') as mock_order_class:
                    mock_order = AsyncMock()
                    mock_order_service = AsyncMock()
                    mock_order_service.get_order_by_id.return_value = Mock(hf_dataset_url="https://hf.co/test/repo")
                    mock_order_class.return_value = mock_order_service

                    result = await service.upload_to_huggingface("test-order", "education")

                    assert result == "https://hf.co/test/repo"

    @pytest.mark.asyncio
    async def test_upload_to_huggingface_fallback(self, service):
        """Test HF upload fallback to script"""
        with patch('app.db.session.async_session_factory') as mock_session_factory:
            mock_session_factory.side_effect = Exception("Delivery service failed")

            with patch.object(service, '_upload_via_script') as mock_fallback:
                mock_fallback.return_value = "https://hf.co/fallback/repo"

                result = await service.upload_to_huggingface("test-order", "education")

                assert result == "https://hf.co/fallback/repo"
                mock_fallback.assert_called_once_with("test-order", "education")

    @pytest.mark.asyncio
    async def test_parse_hf_upload_result(self, service):
        """Test HF upload result parsing"""
        output = """
        Uploading to repository: https://huggingface.co/user/test-dataset
        Upload completed successfully!
        View at: https://huggingface.co/datasets/user/test-dataset
        """

        result = await service._parse_hf_upload_result(output)
        # The parsing logic looks for lines containing the URL pattern
        assert "https://huggingface.co/datasets/user/test-dataset" in result

    @pytest.mark.asyncio
    async def test_parse_hf_upload_result_no_url(self, service):
        """Test HF upload result parsing when no URL found"""
        output = "Upload completed but no URL in output"

        result = await service._parse_hf_upload_result(output)
        assert "huggingface.co/datasets/finedata-production" in result
