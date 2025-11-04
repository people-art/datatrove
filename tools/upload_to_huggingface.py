#!/usr/bin/env python3
"""
FineWeb-Data Dataset Uploader to HuggingFace

This script uploads processed FineWeb-Data datasets to HuggingFace Hub.
Supports domain-specific datasets with proper privacy and licensing settings.
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

try:
    from huggingface_hub import HfApi, login, create_repo
    from datasets import Dataset, DatasetDict, load_dataset
    import pandas as pd
    import boto3
except ImportError as e:
    print(f"Missing required packages. Please install: {e}")
    print("Run: pip install huggingface_hub datasets pandas boto3 python-dotenv")
    exit(1)

# Load environment variables from .env file in project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Upload FineWeb-Data dataset to HuggingFace Hub')

    parser.add_argument('--input-dir', required=True,
                       help='Directory containing the processed dataset files (S3: s3://bucket/path or local: /path/to/dir)')

    parser.add_argument('--repo-name', required=True,
                       help='HuggingFace repository name (e.g., username/fineweb-data-education)')

    parser.add_argument('--token', help='HuggingFace API token')

    parser.add_argument('--private', action='store_true',
                       help='Make the repository private (recommended for production)')

    parser.add_argument('--domain', help='Domain of the dataset (for metadata and naming)')

    parser.add_argument('--merge-files', action='store_true', default=True,
                       help='Merge all JSONL files into a single dataset')

    parser.add_argument('--dump-id', default='CC-MAIN-2024-18',
                       help='Common Crawl dump ID used for processing')

    parser.add_argument('--description', help='Dataset description')

    parser.add_argument('--license', default='apache-2.0',
                       help='Dataset license (default: apache-2.0)')

    parser.add_argument('--max-files', type=int, default=1000,
                       help='Maximum number of files to process (for testing)')

    parser.add_argument('--batch-size', type=int, default=10000,
                       help='Batch size for processing files')

    return parser.parse_args()


def get_s3_files(s3_path: str, max_files: int = 1000) -> List[str]:
    """
    Get list of files from S3 path.

    Args:
        s3_path: S3 path like 's3://bucket/path/'
        max_files: Maximum number of files to return

    Returns:
        List of S3 file paths
    """
    if not s3_path.startswith('s3://'):
        return []

    # Parse S3 path
    path_parts = s3_path.replace('s3://', '').split('/')
    bucket = path_parts[0]
    prefix = '/'.join(path_parts[1:])

    # Use authenticated access for private buckets
    s3_client = boto3.client('s3')

    paginator = s3_client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

    files = []
    for page in page_iterator:
        if 'Contents' in page:
            for obj in page['Contents']:
                key = obj['Key']
                if key.endswith('.jsonl.gz'):
                    files.append(f's3://{bucket}/{key}')
                    if len(files) >= max_files:
                        break
        if len(files) >= max_files:
            break

    return files


def get_local_files(local_path: str, max_files: int = 1000) -> List[str]:
    """
    Get list of local files.

    Args:
        local_path: Local directory path
        max_files: Maximum number of files to return

    Returns:
        List of local file paths
    """
    path = Path(local_path)
    if not path.exists():
        return []

    files = []
    for file_path in path.glob('**/*.jsonl.gz'):
        files.append(str(file_path))
        if len(files) >= max_files:
            break

    return files


def load_jsonl_files(file_paths: List[str], batch_size: int = 10000) -> pd.DataFrame:
    """
    Load and merge JSONL files into a pandas DataFrame.

    Args:
        file_paths: List of file paths (S3 or local)
        batch_size: Batch size for processing

    Returns:
        Combined DataFrame
    """
    all_data = []

    for file_path in file_paths:
        print(f"Loading {file_path}...")
        try:
            if file_path.startswith('s3://'):
                # Load from S3 with authentication
                s3_client = boto3.client('s3')
                path_parts = file_path.replace('s3://', '').split('/')
                bucket = path_parts[0]
                key = '/'.join(path_parts[1:])

                obj = s3_client.get_object(Bucket=bucket, Key=key)
                content = obj['Body'].read().decode('utf-8')
                lines = content.strip().split('\n')
            else:
                # Load from local file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.strip().split('\n')

            # Parse JSON lines
            batch = []
            for line in lines:
                if line.strip():
                    try:
                        batch.append(json.loads(line))
                        if len(batch) >= batch_size:
                            all_data.extend(batch)
                            batch = []
                    except json.JSONDecodeError as e:
                        print(f"Warning: Failed to parse line in {file_path}: {e}")
                        continue

            # Add remaining batch
            if batch:
                all_data.extend(batch)

        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue

    if not all_data:
        raise ValueError("No data loaded from files")

    return pd.DataFrame(all_data)


def create_dataset_card(args, stats: Dict[str, Any]) -> str:
    """
    Create a dataset card with metadata and statistics.

    Args:
        args: Parsed command line arguments
        stats: Dataset statistics

    Returns:
        Dataset card content as string
    """
    domain_info = f" for {args.domain}" if args.domain else ""

    card = f"""---
license: {args.license}
task_categories:
- text-generation
- fill-mask
language:
- en
tags:
- fineweb-data
- common-crawl
- web-scraping
- text-dataset
{"- " + args.domain.replace(' ', '-').lower() if args.domain else ""}
size_categories:
- {stats.get('size_category', 'unknown')}
---

# FineWeb-Data{domain_info}

This dataset is part of the FineWeb-Data collection, processed from Common Crawl data using domain-specific filtering and quality heuristics.

## Dataset Details

- **Source**: Common Crawl {args.dump_id}
- **Domain**: {args.domain or 'General web content'}
- **Processing**: Domain-aware filtering with quality heuristics
- **License**: {args.license}

## Statistics

- **Total documents**: {stats.get('total_documents', 'N/A')}
- **Total tokens**: {stats.get('total_tokens', 'N/A')}
- **Average document length**: {stats.get('avg_doc_length', 'N/A')} tokens
- **Language**: English (filtered)

## Data Format

Each example contains:
- `text`: The processed document text
- `url`: Original URL (PII-redacted)
- `dump`: Common Crawl dump identifier
- `dataset`: Dataset identifier

## Processing Pipeline

1. **Domain Ontology Generation**: LLM-powered ontology creation for target domain
2. **Content Filtering**: Multi-layer filtering including domain relevance, quality, and deduplication
3. **PII Redaction**: Personal information removal for privacy compliance
4. **Quality Assurance**: Gopher, C4, and FineWeb quality filters

## Usage

```python
from datasets import load_dataset

dataset = load_dataset("{args.repo_name}")
```

## Citation

```
@dataset{{fineweb_data{domain_info.replace(' ', '_').lower()},
  title={{FineWeb-Data{domain_info}}},
  author={{FineWeb-Data Team}},
  year={{2024}},
  url={{https://huggingface.co/datasets/{args.repo_name}}}
}}
```
"""

    return card


def main():
    args = parse_args()

    # Authenticate with HuggingFace
    token = args.token or os.getenv('HF_TOKEN')
    if not token:
        raise ValueError("HuggingFace token not provided. Use --token or set HF_TOKEN environment variable")

    login(token)
    api = HfApi()

    print(f"🚀 Uploading FineWeb-Data to {args.repo_name}")

    # Get file list
    if args.input_dir.startswith('s3://'):
        files = get_s3_files(args.input_dir, args.max_files)
    else:
        files = get_local_files(args.input_dir, args.max_files)

    if not files:
        raise ValueError(f"No .jsonl.gz files found in {args.input_dir}")

    print(f"📁 Found {len(files)} files to process")

    # Load and merge data
    print("📖 Loading and merging data...")
    df = load_jsonl_files(files, args.batch_size)

    # Basic statistics
    stats = {
        'total_documents': len(df),
        'total_tokens': df.get('token_count', pd.Series([0]*len(df))).sum(),
        'avg_doc_length': df.get('token_count', pd.Series([0]*len(df))).mean(),
        'size_category': '10K<n<100K' if len(df) < 100000 else '100K<n<1M' if len(df) < 1000000 else '1M<n<10M'
    }

    print(f"📊 Dataset statistics:")
    print(f"  - Documents: {stats['total_documents']:,}")
    print(f"  - Total tokens: {stats['total_tokens']:,}")
    print(f"  - Avg doc length: {stats['avg_doc_length']:.0f} tokens")

    # Convert to HuggingFace dataset
    dataset = Dataset.from_pandas(df)

    # Create repository if it doesn't exist
    try:
        api.repo_info(args.repo_name)
        print(f"📦 Repository {args.repo_name} already exists")
    except Exception:
        print(f"📦 Creating repository {args.repo_name}")
        create_repo(
            args.repo_name,
            token=token,
            private=args.private,
            repo_type="dataset"
        )

    # Create dataset card
    dataset_card = create_dataset_card(args, stats)

    # Upload dataset
    print("⬆️  Uploading dataset...")
    dataset.push_to_hub(
        args.repo_name,
        token=token,
        private=args.private
    )

    # Upload dataset card
    print("📝 Uploading dataset card...")
    api.upload_file(
        path_or_fileobj=dataset_card.encode(),
        path_in_repo="README.md",
        repo_id=args.repo_name,
        token=token
    )

    print(f"✅ Successfully uploaded FineWeb-Data to https://huggingface.co/datasets/{args.repo_name}")
    print(f"📊 Final statistics: {stats['total_documents']:,} documents, {stats['total_tokens']:,} tokens")


if __name__ == '__main__':
    main()
