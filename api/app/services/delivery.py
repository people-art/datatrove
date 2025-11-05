"""
Dataset delivery service for HuggingFace uploads and notifications
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

try:
    from huggingface_hub import HfApi, create_repo
    from datasets import Dataset, DatasetDict
    import boto3
    import botocore
except ImportError:
    HfApi = None
    create_repo = None
    Dataset = None
    DatasetDict = None
    boto3 = None
    botocore = None

from app.core.config import settings
from app.models.benchmark import OrderStatus
from app.services.order import OrderService
from app.services.email import EmailService

logger = structlog.get_logger(__name__)


class DeliveryService:
    """Service for delivering processed datasets to customers."""

    def __init__(self):
        if not all([HfApi, Dataset, boto3]):
            logger.warning("HuggingFace and AWS dependencies not available")
            self.hf_api = None
            self.s3_client = None
        else:
            # Initialize HuggingFace API
            self.hf_api = HfApi(token=settings.HF_TOKEN)

            # Initialize S3 client
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_DEFAULT_REGION
            )

        self.email_service = EmailService()

    async def deliver_dataset(self, order_id: str, db: AsyncSession) -> None:
        """Deliver processed dataset to customer via HuggingFace."""

        try:
            order_service = OrderService(db)
            order = await order_service.get_order_by_id(order_id)

            if not order:
                logger.error("Order not found for delivery", order_id=order_id)
                return

            # Get benchmark job details
            benchmark_job = order.benchmark_job

            # Create HuggingFace repository
            repo_name = await self._create_hf_repo(order_id, benchmark_job.domain)

            # Upload dataset to HuggingFace
            dataset_url = await self._upload_to_huggingface(
                order_id, repo_name, benchmark_job.domain
            )

            # Generate dataset card
            dataset_card_url = await self._create_dataset_card(repo_name, order, benchmark_job)

            # Generate invoice
            invoice_url = await self._generate_invoice(order_id, order)

            # Update order with delivery information
            await order_service.update_order_status(
                order_id,
                OrderStatus.DELIVERED,
                hf_dataset_url=dataset_url,
                dataset_card_url=dataset_card_url,
                invoice_url=invoice_url
            )

            # Send delivery notification email
            await self._send_delivery_email(order, benchmark_job, dataset_url)

            logger.info(
                "Dataset delivered successfully",
                order_id=order_id,
                hf_repo=repo_name,
                dataset_url=dataset_url
            )

        except Exception as e:
            logger.error(
                "Dataset delivery failed",
                order_id=order_id,
                error=str(e)
            )

            # Update order status to failed
            order_service = OrderService(db)
            await order_service.update_order_status(
                order_id,
                OrderStatus.FAILED,
                error_message=f"Delivery failed: {str(e)}"
            )

            raise

    async def _create_hf_repo(self, order_id: str, domain: str) -> str:
        """Create a private HuggingFace repository for the dataset."""

        if not self.hf_api:
            raise Exception("HuggingFace API not available")

        # Generate repository name
        domain_slug = domain.replace(' ', '-').replace('_', '-').lower()
        repo_name = f"{settings.HF_ORG_NAME or 'finedata'}/finedata-{domain_slug}-{order_id[:8]}"

        try:
            # Create private repository
            create_repo(
                repo_name,
                token=settings.HF_TOKEN,
                private=True,
                repo_type="dataset",
                exist_ok=True
            )

            logger.info("HuggingFace repository created", repo_name=repo_name)
            return repo_name

        except Exception as e:
            logger.error("Failed to create HF repository", repo_name=repo_name, error=str(e))
            raise

    async def _upload_to_huggingface(
        self,
        order_id: str,
        repo_name: str,
        domain: str
    ) -> str:
        """Upload processed dataset to HuggingFace Hub."""

        if not all([self.hf_api, Dataset, self.s3_client]):
            raise Exception("Required dependencies not available")

        try:
            # Download dataset from S3
            dataset_files = await self._download_from_s3(order_id)

            if not dataset_files:
                raise Exception("No dataset files found in S3")

            # Create dataset from files
            dataset = await self._create_dataset_from_files(dataset_files, domain)

            # Upload to HuggingFace
            dataset.push_to_hub(
                repo_name,
                token=settings.HF_TOKEN,
                private=True
            )

            dataset_url = f"https://huggingface.co/datasets/{repo_name}"
            logger.info("Dataset uploaded to HuggingFace", repo_name=repo_name, url=dataset_url)

            return dataset_url

        except Exception as e:
            logger.error("Failed to upload to HuggingFace", repo_name=repo_name, error=str(e))
            raise

    async def _download_from_s3(self, order_id: str) -> List[Path]:
        """Download processed dataset files from S3."""

        if not self.s3_client:
            raise Exception("S3 client not available")

        try:
            local_dir = Path(f"/tmp/finedata-delivery/{order_id}")
            local_dir.mkdir(parents=True, exist_ok=True)

            # List objects in the production bucket with order prefix
            prefix = f"production/{order_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=settings.S3_BUCKET_DATASETS,
                Prefix=prefix
            )

            downloaded_files = []

            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    if key.endswith('.jsonl.gz'):
                        local_file = local_dir / Path(key).name

                        # Download file
                        self.s3_client.download_file(
                            settings.S3_BUCKET_DATASETS,
                            key,
                            str(local_file)
                        )

                        downloaded_files.append(local_file)
                        logger.info("Downloaded dataset file", file=str(local_file))

            return downloaded_files

        except Exception as e:
            logger.error("Failed to download from S3", order_id=order_id, error=str(e))
            raise

    async def _create_dataset_from_files(self, files: List[Path], domain: str) -> Dataset:
        """Create HuggingFace dataset from downloaded files."""

        if not Dataset:
            raise Exception("Datasets library not available")

        try:
            # Load all JSONL files
            data = []
            for file_path in files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            record = json.loads(line.strip())
                            data.append(record)
                        except json.JSONDecodeError:
                            continue

            # Create dataset
            dataset = Dataset.from_list(data)

            # Add metadata
            dataset = dataset.add_column("domain", [domain] * len(dataset))
            dataset = dataset.add_column("source", ["finedata"] * len(dataset))

            logger.info("Dataset created from files", file_count=len(files), record_count=len(data))
            return dataset

        except Exception as e:
            logger.error("Failed to create dataset from files", error=str(e))
            raise

    async def _create_dataset_card(self, repo_name: str, order, benchmark_job) -> str:
        """Create and upload dataset card to HuggingFace."""

        if not self.hf_api:
            raise Exception("HuggingFace API not available")

        try:
            # Generate dataset card content
            card_content = self._generate_dataset_card_content(order, benchmark_job)

            # Upload to repository
            self.hf_api.upload_file(
                path_or_fileobj=card_content.encode(),
                path_in_repo="README.md",
                repo_id=repo_name,
                repo_type="dataset"
            )

            card_url = f"https://huggingface.co/datasets/{repo_name}/blob/main/README.md"
            logger.info("Dataset card created", repo_name=repo_name, url=card_url)

            return card_url

        except Exception as e:
            logger.error("Failed to create dataset card", repo_name=repo_name, error=str(e))
            raise

    def _generate_dataset_card_content(self, order, benchmark_job) -> str:
        """Generate dataset card content in markdown format."""

        return f"""---
license: other
task_categories:
- text-generation
language:
- {', '.join(benchmark_job.languages)}
tags:
- finedata
- {benchmark_job.domain.replace(' ', '-')}
- dataset
size_categories:
- {len(order.final_tokens) if order.final_tokens else 'unknown'}
---

# FineData: {benchmark_job.domain.title()} Dataset

This dataset was generated by FineData using advanced web crawling, filtering, and quality assessment techniques.

## Dataset Details

- **Domain**: {benchmark_job.domain}
- **Languages**: {', '.join(benchmark_job.languages)}
- **Time Range**: {benchmark_job.time_range_start} to {benchmark_job.time_range_end}
- **Quality Tier**: {benchmark_job.quality_tier}
- **Total Tokens**: {order.final_tokens:, if order.final_tokens else 'Processing'}
- **Total Documents**: {order.final_docs:, if hasattr(order, 'final_docs') and order.final_docs else 'Processing'}

## Generation Process

This dataset was created through the following pipeline:

1. **Web Crawling**: Collected from Common Crawl dumps
2. **Content Extraction**: Using Trafilatura for clean text extraction
3. **Language Filtering**: Limited to specified languages
4. **Domain Relevance**: Filtered using LLM-powered ontology matching
5. **Quality Assessment**: Multi-layer quality filters and deduplication
6. **Privacy Protection**: PII removal and content sanitization

## Usage

```python
from datasets import load_dataset

dataset = load_dataset("{settings.HF_ORG_NAME or 'finedata'}/finedata-{benchmark_job.domain.replace(' ', '-')}", split="train")
```

## Citation

If you use this dataset in your research, please cite:

```
@dataset{{finedata_{benchmark_job.domain.replace(' ', '_')},
  title={{FineData: {benchmark_job.domain.title()} Dataset}},
  author={{FineData}},
  year={{2024}},
  url={{https://huggingface.co/datasets/{settings.HF_ORG_NAME or 'finedata'}/finedata-{benchmark_job.domain.replace(' ', '-')}}}
}}
```

## License

This dataset is provided for internal training purposes only. Redistribution is not permitted without explicit permission from FineData.

## Contact

For questions or support, please contact support@finedata.example.com
"""

    async def _generate_invoice(self, order_id: str, order) -> str:
        """Generate and upload invoice PDF."""

        try:
            # For now, create a simple text invoice
            # In production, this would generate a proper PDF invoice
            invoice_content = self._generate_invoice_content(order_id, order)

            # Upload to S3 (in production, this would be a proper invoice service)
            invoice_key = f"invoices/{order_id}.txt"
            self.s3_client.put_object(
                Bucket=settings.S3_BUCKET_DATASETS,
                Key=invoice_key,
                Body=invoice_content.encode(),
                ContentType='text/plain'
            )

            invoice_url = f"https://{settings.S3_BUCKET_DATASETS}.s3.amazonaws.com/{invoice_key}"
            logger.info("Invoice generated", order_id=order_id, url=invoice_url)

            return invoice_url

        except Exception as e:
            logger.error("Failed to generate invoice", order_id=order_id, error=str(e))
            raise

    def _generate_invoice_content(self, order_id: str, order) -> str:
        """Generate invoice content."""

        return f"""
FineData Dataset Generation Invoice

Order ID: {order_id}
Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Description: Custom {order.benchmark_job.domain} dataset generation
Quality Tier: {order.benchmark_job.quality_tier}

Amount: ${order.total:.2f} USD
Tax: ${order.tax:.2f} USD
Total: ${order.total + order.tax:.2f} USD

Payment Status: {'Paid' if order.status == OrderStatus.PAID else 'Pending'}

Thank you for using FineData!
"""

    async def _send_delivery_email(self, order, benchmark_job, dataset_url: str) -> None:
        """Send dataset delivery notification email."""

        try:
            subject = f"Your FineData {benchmark_job.domain} Dataset is Ready!"

            body = f"""
Dear Customer,

Your custom dataset for "{benchmark_job.domain}" has been successfully processed and is now available!

📊 Dataset Details:
- Domain: {benchmark_job.domain}
- Languages: {', '.join(benchmark_job.languages)}
- Quality Tier: {benchmark_job.quality_tier}
- Estimated Tokens: {order.final_tokens:, if order.final_tokens else 'Processing'}

🔗 Dataset Access:
{dataset_url}

📄 Dataset Card:
{dataset_url}/blob/main/README.md

🧾 Invoice:
{order.invoice_url}

⚠️ Important Notes:
- This dataset is stored in a private HuggingFace repository
- Access is restricted to your account only
- The dataset may only be used for internal training purposes
- Contact support if you need to share access with team members

If you have any questions or need assistance, please don't hesitate to contact our support team.

Best regards,
The FineData Team
support@finedata.example.com
"""

            await self.email_service.send_email(
                to_email=benchmark_job.email,
                subject=subject,
                body=body
            )

            logger.info("Delivery email sent", order_id=order.id, email=benchmark_job.email)

        except Exception as e:
            logger.error("Failed to send delivery email", order_id=order.id, error=str(e))
            # Don't raise exception for email failures - delivery is still successful
