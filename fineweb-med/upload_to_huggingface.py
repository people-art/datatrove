#!/usr/bin/env python3
"""
FineWeb-Med Dataset Uploader to HuggingFace

This script uploads the processed FineWeb-Med dataset to HuggingFace Hub.
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

try:
    from huggingface_hub import HfApi, login, create_repo
    from datasets import Dataset, DatasetDict, load_dataset
    import pandas as pd
except ImportError as e:
    print(f"Missing required packages. Please install: {e}")
    print("Run: pip install huggingface_hub datasets pandas")
    exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Upload FineWeb-Med dataset to HuggingFace Hub')

    parser.add_argument('--input-dir', required=True,
                       help='Directory containing the processed dataset files')

    parser.add_argument('--repo-name', required=True,
                       help='HuggingFace repository name (e.g., username/fineweb-med)')

    parser.add_argument('--token', help='HuggingFace API token')

    parser.add_argument('--private', action='store_true',
                       help='Make the repository private')

    parser.add_argument('--merge-files', action='store_true', default=True,
                       help='Merge all JSONL files into a single dataset')

    parser.add_argument('--dump-id', default='CC-MAIN-2023-50',
                       help='Common Crawl dump ID used for processing')

    return parser.parse_args()


def count_total_documents(input_dir: str) -> int:
    """Count total number of documents in all JSONL files."""
    import gzip

    total_docs = 0
    input_path = Path(input_dir)

    for jsonl_file in input_path.glob("*.jsonl.gz"):
        with gzip.open(jsonl_file, 'rt', encoding='utf-8') as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    total_docs += 1

    return total_docs


def create_dataset_card(repo_name: str, dump_id: str, total_docs: int, total_tokens: int) -> str:
    """Create a dataset card with metadata."""

    card_content = f"""---
dataset_info:
  features:
  - name: text
    dtype: string
  - name: id
    dtype: string
  - name: metadata
    dtype:
      dump: string
      dataset: string
      url: string
      date: string
      file_path: string
      language: string
      language_score: float64
      token_count: int64
  configs:
  - config_name: default
    data_files:
    - split: train
      path: data/train-*
language: en
license: apache-2.0
task_categories:
- text-generation
- fill-mask
- text-classification
- question-answering
- summarization
size_categories:
- {get_size_category(total_docs)}
---

# FineWeb-Med: Medical-Focused Web Dataset

FineWeb-Med is a high-quality dataset of medical and healthcare-related web content, extracted and processed from Common Crawl using the FineWeb methodology.

## Dataset Summary

This dataset contains **{total_docs:,} documents** with approximately **{total_tokens:,} tokens**, focusing on medical, healthcare, and related topics from the web.

## Data Processing

The dataset was created using the following processing pipeline:

1. **Data Source**: Common Crawl dump `{dump_id}`
2. **Text Extraction**: Trafilatura for high-quality text extraction
3. **Language Filtering**: Only English content retained
4. **Medical Content Filtering**: Documents must contain at least one of 26 medical keywords
5. **Length Filtering**: Documents must be at least 200 words
6. **Quality Filtering**:
   - Gopher repetition filtering
   - Gopher quality filtering
   - C4 quality filtering
   - FineWeb quality filtering
7. **Token Counting**: Using GPT-2 tokenizer

## Medical Keywords

The dataset filters for documents containing any of these medical keywords:
- medical, diagnosis, treatment, patient, doctor, symptom, therapy
- prescription, clinical, healthcare, medicine, pharmaceutical
- hospital, clinic, nurse, surgery, disease, disorder, condition
- medication, drug, vaccine, epidemic, pandemic, health, wellness

## Data Format

Each example is a JSON object with the following fields:

- `text`: The extracted and cleaned text content
- `id`: Unique identifier from the original WARC record
- `metadata`: Dictionary containing:
  - `dump`: Common Crawl dump identifier
  - `dataset`: Dataset name ("fineweb-med")
  - `url`: Original webpage URL
  - `date`: Crawl timestamp
  - `file_path`: S3 path to source WARC file
  - `language`: Detected language (always "en")
  - `language_score`: Language detection confidence
  - `token_count`: Number of tokens in the text

## Usage

```python
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("{repo_name}")

# Access the data
for example in dataset['train']:
    print(example['text'])
    print(example['metadata'])
```

## Statistics

- **Total Documents**: {total_docs:,}
- **Approximate Tokens**: {total_tokens:,}
- **Average Tokens per Document**: {total_tokens // total_docs if total_docs > 0 else 0:,}
- **Source Dump**: {dump_id}
- **Language**: English only

## License

This dataset is released under the Apache 2.0 license.

## Citation

```
@dataset{{fineweb_med,
  title={{FineWeb-Med: Medical-Focused Web Dataset}},
  author={{Generated using datatrove FineWeb methodology}},
  year={{2024}}
}}
```
"""

    return card_content


def get_size_category(num_docs: int) -> str:
    """Get size category based on number of documents."""
    if num_docs < 1000:
        return "n<1K"
    elif num_docs < 10000:
        return "1K<n<10K"
    elif num_docs < 100000:
        return "10K<n<100K"
    elif num_docs < 1000000:
        return "100K<n<1M"
    else:
        return "n>1M"


def merge_jsonl_files(input_dir: str, output_file: str):
    """Merge all JSONL files into a single file."""
    import gzip

    input_path = Path(input_dir)

    with gzip.open(output_file, 'wt', encoding='utf-8') as outfile:
        for jsonl_file in sorted(input_path.glob("*.jsonl.gz")):
            print(f"Merging {jsonl_file.name}...")
            with gzip.open(jsonl_file, 'rt', encoding='utf-8') as infile:
                for line in infile:
                    if line.strip():  # Skip empty lines
                        outfile.write(line)


def upload_to_huggingface(input_dir: str, repo_name: str, token: str = None,
                         private: bool = False, merge_files: bool = True):
    """Upload the dataset to HuggingFace Hub."""

    # Set up authentication
    if token:
        login(token=token)

    api = HfApi()

    # Create repository if it doesn't exist
    try:
        create_repo(repo_name, token=token, private=private, repo_type="dataset")
        print(f"Created repository: {repo_name}")
    except Exception as e:
        print(f"Repository {repo_name} already exists or error: {e}")

    # Count documents and estimate tokens
    total_docs = count_total_documents(input_dir)
    # Rough estimate: average ~800 tokens per document based on our sample
    estimated_tokens = total_docs * 800

    print(f"Dataset statistics:")
    print(f"  Total documents: {total_docs:,}")
    print(f"  Estimated tokens: {estimated_tokens:,}")

    if merge_files:
        # Merge all files into a single dataset
        print("Merging JSONL files...")
        merged_file = f"{input_dir}/merged_dataset.jsonl.gz"
        merge_jsonl_files(input_dir, merged_file)

        # Create dataset from merged file
        print("Creating HuggingFace dataset...")
        dataset = load_dataset("json", data_files=merged_file, split="train")

        # Upload to HuggingFace
        print(f"Uploading to {repo_name}...")
        dataset.push_to_hub(repo_name, token=token, private=private)

        # Clean up merged file
        os.remove(merged_file)
    else:
        # Upload individual files
        print("Uploading individual files...")
        for file_path in Path(input_dir).glob("*.jsonl.gz"):
            file_name = file_path.name
            print(f"Uploading {file_name}...")
            api.upload_file(
                path_or_fileobj=str(file_path),
                path_in_repo=f"data/{file_name}",
                repo_id=repo_name,
                repo_type="dataset",
                token=token
            )

    # Create and upload dataset card
    print("Creating dataset card...")
    dataset_card = create_dataset_card(repo_name, "CC-MAIN-2023-50", total_docs, estimated_tokens)

    api.upload_file(
        path_or_fileobj=dataset_card.encode('utf-8'),
        path_in_repo="README.md",
        repo_id=repo_name,
        repo_type="dataset",
        token=token
    )

    print("✅ Upload completed successfully!")
    print(f"📊 Dataset available at: https://huggingface.co/datasets/{repo_name}")
    print(f"📈 {total_docs:,} documents uploaded")


def main():
    args = parse_args()

    # Validate input directory
    if not os.path.exists(args.input_dir):
        print(f"Error: Input directory {args.input_dir} does not exist")
        exit(1)

    # Check for JSONL files
    jsonl_files = list(Path(args.input_dir).glob("*.jsonl.gz"))
    if not jsonl_files:
        print(f"Error: No .jsonl.gz files found in {args.input_dir}")
        exit(1)

    print(f"Found {len(jsonl_files)} JSONL files to upload")
    print(f"Target repository: {args.repo_name}")
    print(f"Merge files: {args.merge_files}")

    # Upload to HuggingFace
    upload_to_huggingface(
        input_dir=args.input_dir,
        repo_name=args.repo_name,
        token=args.token,
        private=args.private,
        merge_files=args.merge_files
    )


if __name__ == "__main__":
    main()
