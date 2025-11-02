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
from dotenv import load_dotenv

try:
    from huggingface_hub import HfApi, login, create_repo
    from datasets import Dataset, DatasetDict, load_dataset
    import pandas as pd
    import boto3
    from botocore import UNSIGNED
    from botocore.client import Config
except ImportError as e:
    print(f"Missing required packages. Please install: {e}")
    print("Run: pip install huggingface_hub datasets pandas boto3 python-dotenv")
    exit(1)

# Load environment variables from .env file in project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Upload FineWeb-Med dataset to HuggingFace Hub')

    parser.add_argument('--input-dir', required=True,
                       help='Directory containing the processed dataset files (S3: s3://bucket/path or local: /path/to/dir)')

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


def is_s3_path(path: str) -> bool:
    """Check if the path is an S3 path."""
    return path.startswith('s3://')


def parse_s3_path(s3_path: str) -> tuple[str, str]:
    """Parse S3 path into bucket and key prefix."""
    if not s3_path.startswith('s3://'):
        raise ValueError("Not an S3 path")

    path_without_scheme = s3_path[5:]  # Remove 's3://'
    bucket, key = path_without_scheme.split('/', 1)
    return bucket, key


def get_s3_client():
    """Get S3 client with credentials if available, otherwise anonymous access."""
    # Try to get credentials from environment
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

    if aws_access_key and aws_secret_key:
        # Use credentials
        return boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=aws_region
        )
    else:
        # Fall back to anonymous access
        print("⚠️  No AWS credentials found, using anonymous access")
        return boto3.client('s3', config=Config(signature_version=UNSIGNED))


def list_s3_files(bucket: str, prefix: str) -> List[str]:
    """List all .jsonl.gz files in S3 bucket with given prefix."""
    s3_client = get_s3_client()
    files = []

    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        if 'Contents' in page:
            for obj in page['Contents']:
                key = obj['Key']
                if key.endswith('.jsonl.gz'):
                    files.append(key)

    return files


def download_s3_file(bucket: str, key: str, local_path: str):
    """Download a file from S3 to local path."""
    s3_client = get_s3_client()
    s3_client.download_file(bucket, key, local_path)


def analyze_dataset(input_dir: str) -> tuple[int, int, dict]:
    """Analyze dataset and return total documents, tokens, and statistics."""
    import gzip
    import json
    import tempfile
    import os

    total_docs = 0
    total_tokens = 0
    token_counts = []
    url_domains = {}
    languages = {}

    if is_s3_path(input_dir):
        # Handle S3 path
        bucket, prefix = parse_s3_path(input_dir)
        s3_files = list_s3_files(bucket, prefix)

        if not s3_files:
            print(f"No .jsonl.gz files found in s3://{bucket}/{prefix}")
            return 0, 0, {}

        print(f"Found {len(s3_files)} files in S3, analyzing...")

        # Create temporary directory for downloads
        with tempfile.TemporaryDirectory() as temp_dir:
            for s3_key in s3_files:
                # Download file to temporary location
                local_file = os.path.join(temp_dir, os.path.basename(s3_key))
                try:
                    download_s3_file(bucket, s3_key, local_file)
                    print(f"Downloaded and analyzing {os.path.basename(s3_key)}...")

                    # Analyze the downloaded file
                    with gzip.open(local_file, 'rt', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():  # Skip empty lines
                                try:
                                    doc = json.loads(line)
                                    total_docs += 1

                                    # Count tokens
                                    token_count = doc.get('metadata', {}).get('token_count', 0)
                                    total_tokens += token_count
                                    token_counts.append(token_count)

                                    # Analyze URLs
                                    url = doc.get('metadata', {}).get('url', '')
                                    if url:
                                        try:
                                            from urllib.parse import urlparse
                                            domain = urlparse(url).netloc
                                            url_domains[domain] = url_domains.get(domain, 0) + 1
                                        except:
                                            pass

                                    # Language stats
                                    lang = doc.get('metadata', {}).get('language', 'unknown')
                                    languages[lang] = languages.get(lang, 0) + 1

                                except json.JSONDecodeError:
                                    continue

                except Exception as e:
                    print(f"Error downloading/analyzing {s3_key}: {e}")
                    continue

    else:
        # Handle local path
        input_path = Path(input_dir)

        for jsonl_file in input_path.glob("*.jsonl.gz"):
            print(f"Analyzing {jsonl_file.name}...")
            with gzip.open(jsonl_file, 'rt', encoding='utf-8') as f:
                for line in f:
                    if line.strip():  # Skip empty lines
                        try:
                            doc = json.loads(line)
                            total_docs += 1

                            # Count tokens
                            token_count = doc.get('metadata', {}).get('token_count', 0)
                            total_tokens += token_count
                            token_counts.append(token_count)

                            # Analyze URLs
                            url = doc.get('metadata', {}).get('url', '')
                            if url:
                                try:
                                    from urllib.parse import urlparse
                                    domain = urlparse(url).netloc
                                    url_domains[domain] = url_domains.get(domain, 0) + 1
                                except:
                                    pass

                            # Language stats
                            lang = doc.get('metadata', {}).get('language', 'unknown')
                            languages[lang] = languages.get(lang, 0) + 1

                        except json.JSONDecodeError:
                            continue

    # Calculate statistics
    stats = {
        'total_docs': total_docs,
        'total_tokens': total_tokens,
        'avg_tokens_per_doc': total_tokens / total_docs if total_docs > 0 else 0,
        'token_distribution': {
            'min': min(token_counts) if token_counts else 0,
            'max': max(token_counts) if token_counts else 0,
            'median': sorted(token_counts)[len(token_counts)//2] if token_counts else 0,
        },
        'top_domains': sorted(url_domains.items(), key=lambda x: x[1], reverse=True)[:10],
        'languages': languages
    }

    return total_docs, total_tokens, stats


def create_dataset_card(repo_name: str, dump_id: str, total_docs: int, total_tokens: int, stats: dict) -> str:
    """Create a comprehensive dataset card with metadata, following FineWeb style."""

    card_content = f"""

# 🍷🏥 FineWeb-Med: Medical-Focused Web Dataset

FineWeb-Med is a high-quality dataset of medical and healthcare-related web content, extracted and processed from Common Crawl using the FineWeb methodology with specialized medical filtering.

## Dataset Summary

This dataset contains **{total_docs:,} documents** with approximately **{total_tokens:,} tokens**, focusing exclusively on medical, healthcare, and related topics from the web. It serves as a specialized complement to general web datasets like FineWeb for training medical AI models.

## Data Processing

The dataset was created using the 🏭 `datatrove` library with enhanced medical-specific processing. You can find the complete processing script in our repository.

### Processing Pipeline

1. **Data Source**: Common Crawl dump `{dump_id}`
2. **URL Filtering**: Remove malicious and NSFW websites using blocklists and subword detection
3. **Text Extraction**: Trafilatura for high-quality text extraction from raw HTML WARC files
4. **Language Filtering**: FastText language detection, keeping only English content (score > 0.65)
5. **Medical Content Filtering**: Documents must contain at least one of 26 medical keywords
6. **Length Filtering**: Documents must be at least 200 words to ensure substantial content
7. **Quality Filtering**:
   - Gopher repetition and quality filters
   - C4 quality filters (excluding terminal punctuation rule)
   - FineWeb custom filters for list-like documents and formatting issues
8. **Token Counting**: GPT-2 tokenizer for token statistics

## Medical Keywords

The dataset employs specialized filtering for medical content using these keywords:

**Core Medical Terms**: medical, diagnosis, treatment, patient, doctor, symptom, therapy, prescription, clinical, healthcare

**Healthcare Facilities**: hospital, clinic, nurse, surgery, pharmacy, pharmaceutical

**Health Conditions**: disease, disorder, condition, medication, drug, vaccine, epidemic, pandemic

**Wellness Terms**: health, wellness

## Data Format

Each example is a JSON object with the following fields:

### Core Fields
- **`text`** *(string)*: The extracted and cleaned text content
- **`id`** *(string)*: Unique identifier from the original WARC record
- **`metadata`** *(dict)*: Extended metadata information

### Metadata Fields
- **`dump`** *(string)*: Common Crawl dump identifier (e.g., "CC-MAIN-2023-50")
- **`dataset`** *(string)*: Dataset identifier ("fineweb-med")
- **`url`** *(string)*: Original webpage URL
- **`date`** *(string)*: Crawl timestamp in ISO format
- **`file_path`** *(string)*: S3 path to source WARC file
- **`language`** *(string)*: Detected language (always "en" for this dataset)
- **`language_score`** *(float)*: Language detection confidence score
- **`token_count`** *(int)*: Number of tokens using GPT-2 tokenizer

## Usage

### Loading the Dataset

```python
from datasets import load_dataset

# Load the complete dataset
dataset = load_dataset("{repo_name}")

# Access training split
train_data = dataset['train']

# Example usage
for example in train_data:
    print(f"Text: {{example['text'][:100]}}...")
    print(f"URL: {{example['metadata']['url']}}")
    print(f"Tokens: {{example['metadata']['token_count']}}")
    break
```

### Medical-Specific Filtering

```python
# Filter for clinical documents
clinical_docs = [doc for doc in dataset['train']
                 if 'clinical' in doc['text'].lower()]

# Filter by token count for model training
suitable_docs = [doc for doc in dataset['train']
                 if 512 <= doc['metadata']['token_count'] <= 2048]
```

## Statistics

| Metric | Value |
|--------|-------|
| **Total Documents** | {total_docs:,} |
| **Total Tokens** | {total_tokens:,} |
| **Average Tokens/Document** | {stats.get('avg_tokens_per_doc', 0):.1f} |
| **Token Range** | {stats.get('token_distribution', {}).get('min', 0):,} - {stats.get('token_distribution', {}).get('max', 0):,} |
| **Median Tokens/Document** | {stats.get('token_distribution', {}).get('median', 0):,} |
| **Source Dump** | {dump_id} |
| **Language** | English only |
| **Medical Focus** | Healthcare & medical content |

### Top Content Sources
{chr(10).join([f"- **{domain}**: {count:,} documents" for domain, count in stats.get('top_domains', [])[:5]])}

## Dataset Creation

### Curation Rationale

While FineWeb provides excellent general web text data, specialized domains like healthcare require targeted datasets. FineWeb-Med addresses this need by applying medical-specific filtering to create a high-quality, domain-focused dataset suitable for:

- Training medical language models
- Fine-tuning healthcare AI applications
- Medical text analysis and NLP research
- Healthcare chatbot development

### Source Data

**Primary Source**: Common Crawl web crawl data
- **Dump**: {dump_id}
- **Time Period**: 2023-2024 web crawl
- **Content Type**: Public web pages with medical relevance

### Annotations

We augment samples with automatic annotations:
- **`language`** & **`language_score`**: Generated by FastText language classifier
- **`token_count`**: Calculated using GPT-2 tokenizer

## Considerations for Using the Data

### Social Impact

This dataset enables more accessible development of healthcare AI applications, potentially improving medical text understanding and patient care through better language models.

### Discussion of Biases

The dataset inherits biases from web-sourced medical content, which may reflect:
- Geographic biases in healthcare information availability
- Language biases (English-only content)
- Platform biases from different healthcare websites

### Limitations

- **Code Content**: Limited due to filtering steps; supplement with code-specific datasets if needed
- **Medical Accuracy**: Web content may contain outdated or inaccurate medical information
- **PII Concerns**: Despite anonymization, some personal health information may remain
- **Specialized Domains**: May not cover all medical specialties equally

## Additional Information

### Licensing Information

**License**: Apache 2.0
**Additional Terms**: Subject to Common Crawl's Terms of Use

### Personal and Sensitive Information

We anonymize:
- Email addresses → `email@example.com` or `firstname.lastname@example.org`
- Public IP addresses → Randomly assigned non-responsive IPs

For PII removal requests, please create an issue in our repository.

### Future Work

We plan to expand FineWeb-Med with:
- Additional medical domains and specialties
- Multi-language medical content
- Enhanced quality filtering for medical text
- Integration with medical knowledge bases

## Citation Information

```bibtex
@dataset{{fineweb_med,
  title={{FineWeb-Med: Medical-Focused Web Dataset}},
  author={{Generated using datatrove FineWeb methodology with medical filtering}},
  year={{2024}},
  url={{https://huggingface.co/datasets/{repo_name}}}
}}
```

---

*Built with ❤️ using the FineWeb methodology and datatrove*
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
    """Merge all JSONL files into a single file. Always outputs to a local file."""
    import gzip
    import tempfile
    import os

    # Always create a local output file, regardless of input source
    local_output_file = output_file
    if is_s3_path(output_file):
        # If output_file is S3 path, create a local temporary file instead
        import tempfile
        temp_fd, local_output_file = tempfile.mkstemp(suffix='.jsonl.gz')
        os.close(temp_fd)  # Close the file descriptor, we'll open it with gzip

    if is_s3_path(input_dir):
        # Handle S3 path
        bucket, prefix = parse_s3_path(input_dir)
        s3_files = list_s3_files(bucket, prefix)

        if not s3_files:
            raise ValueError(f"No .jsonl.gz files found in s3://{bucket}/{prefix}")

        print(f"Merging {len(s3_files)} files from S3...")

        # Create temporary directory for downloads
        with tempfile.TemporaryDirectory() as temp_dir:
            with gzip.open(local_output_file, 'wt', encoding='utf-8') as outfile:
                for s3_key in sorted(s3_files):
                    # Download file to temporary location
                    local_file = os.path.join(temp_dir, os.path.basename(s3_key))
                    try:
                        download_s3_file(bucket, s3_key, local_file)
                        print(f"Merging {os.path.basename(s3_key)}...")

                        # Merge the downloaded file
                        with gzip.open(local_file, 'rt', encoding='utf-8') as infile:
                            for line in infile:
                                if line.strip():  # Skip empty lines
                                    outfile.write(line)

                    except Exception as e:
                        print(f"Error downloading/merging {s3_key}: {e}")
                        continue

    else:
        # Handle local path
        input_path = Path(input_dir)

        with gzip.open(local_output_file, 'wt', encoding='utf-8') as outfile:
            for jsonl_file in sorted(input_path.glob("*.jsonl.gz")):
                print(f"Merging {jsonl_file.name}...")
                with gzip.open(jsonl_file, 'rt', encoding='utf-8') as infile:
                    for line in infile:
                        if line.strip():  # Skip empty lines
                            outfile.write(line)

    # Return the actual local file path used
    return local_output_file


def upload_to_huggingface(input_dir: str, repo_name: str, token: str = None,
                         private: bool = False, merge_files: bool = True, dump_id: str = "CC-MAIN-2023-50"):
    """Upload the dataset to HuggingFace Hub."""

    # Set up authentication with retry
    if token:
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                login(token=token)
                break
            except Exception as e:
                if "429" in str(e) or "Too Many Requests" in str(e):
                    if attempt < max_retries - 1:
                        wait_time = 30 * (attempt + 1)  # Progressive backoff
                        print(f"⚠️  Rate limited, waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                    else:
                        print(f"❌ Authentication failed after {max_retries} attempts: {e}")
                        raise e
                else:
                    print(f"❌ Authentication failed: {e}")
                    raise e

    api = HfApi()

    # Validate repository name format
    if '/' not in repo_name:
        print("❌ Error: Repository name must be in format 'username/dataset-name'")
        print(f"   Got: {repo_name}")
        print("   Example: your-username/fineweb-med")
        exit(1)

    username = repo_name.split('/')[0]
    print(f"📝 Target username: {username}")
    print(f"📦 Repository: {repo_name}")

    # Check if user can access/create repositories under this namespace
    max_retries = 3
    user_info = None
    for attempt in range(max_retries):
        try:
            # Try to get user info to validate token and username
            user_info = api.whoami(token=token)
            print(f"✅ Authenticated as: {user_info['name']}")
            break
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                if attempt < max_retries - 1:
                    wait_time = 30 * (attempt + 1)
                    print(f"⚠️  Rate limited during whoami, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Failed to get user info after {max_retries} attempts: {e}")
                    exit(1)
            else:
                print(f"❌ Authentication failed: {e}")
                print("   Please check your HuggingFace token.")
                exit(1)

    # Check if the username matches
    if user_info and user_info['name'] != username:
        print(f"⚠️  Warning: Authenticated username '{user_info['name']}' doesn't match target '{username}'")
        print("   This may cause permission issues. Consider using your actual username.")

    # Create repository if it doesn't exist
    repo_created = False
    for attempt in range(max_retries):
        try:
            create_repo(repo_name, token=token, private=private, repo_type="dataset")
            print(f"✅ Created repository: {repo_name}")
            repo_created = True
            break
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Too Many Requests" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = 30 * (attempt + 1)
                    print(f"⚠️  Rate limited during repo creation, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"⚠️  Repository creation failed after {max_retries} attempts: {e}")
                    print("   Will attempt to upload to existing repository...")
            elif "403" in error_msg or "Forbidden" in error_msg:
                print(f"❌ Permission denied: Cannot create repository under '{username}' namespace")
                print("   Possible solutions:")
                print(f"   1. Change username to your actual HF username: {user_info.get('name', 'unknown') if user_info else 'unknown'}")
                print("   2. Check your token permissions at: https://huggingface.co/settings/tokens")
                print("   3. Make sure you have 'Write' permissions for dataset creation")
                exit(1)
            elif "already exists" in error_msg.lower() or "409" in error_msg or "Conflict" in error_msg:
                print(f"ℹ️  Repository {repo_name} already exists, will update it")
                repo_created = True
                break
            else:
                if attempt < max_retries - 1:
                    wait_time = 30 * (attempt + 1)
                    print(f"⚠️  Repository creation issue: {e}")
                    print(f"   Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"⚠️  Repository creation failed after {max_retries} attempts: {e}")
                    print("   Will attempt to upload to existing repository...")
                    break

    # Analyze dataset for detailed statistics
    print("Analyzing dataset...")
    total_docs, total_tokens, stats = analyze_dataset(input_dir)

    print(f"Dataset statistics:")
    print(f"  Total documents: {total_docs:,}")
    print(f"  Total tokens: {total_tokens:,}")
    print(f"  Average tokens/doc: {stats.get('avg_tokens_per_doc', 0):.1f}")
    print(f"  Token range: {stats.get('token_distribution', {}).get('min', 0):,} - {stats.get('token_distribution', {}).get('max', 0):,}")
    if stats.get('top_domains'):
        print(f"  Top domains: {', '.join([f'{d}({c})' for d, c in stats['top_domains'][:3]])}")

    if merge_files:
        # Merge all files into a single dataset
        print("Merging JSONL files...")
        merged_file = f"{input_dir}/merged_dataset.jsonl.gz"
        actual_merged_file = merge_jsonl_files(input_dir, merged_file)

        # Create dataset from merged file
        print("Creating HuggingFace dataset...")
        dataset = load_dataset("json", data_files=actual_merged_file, split="train")

        # Delete existing README.md if it exists (to avoid malformed YAML)
        try:
            api.delete_file("README.md", repo_id=repo_name, repo_type="dataset", token=token)
            print("Removed existing README.md")
        except Exception:
            pass  # README.md doesn't exist, which is fine

        # Upload to HuggingFace
        print(f"Uploading to {repo_name}...")
        dataset.push_to_hub(repo_name, token=token, private=private)

        # Clean up merged file
        os.remove(actual_merged_file)
    else:
        # Upload individual files
        print("Uploading individual files...")

        if is_s3_path(input_dir):
            # Handle S3 path
            bucket, prefix = parse_s3_path(input_dir)
            s3_files = list_s3_files(bucket, prefix)

            if not s3_files:
                print(f"No .jsonl.gz files found in s3://{bucket}/{prefix}")
                return

            print(f"Found {len(s3_files)} files in S3 to upload")

            # Create temporary directory for downloads
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                for s3_key in s3_files:
                    file_name = os.path.basename(s3_key)
                    local_file = os.path.join(temp_dir, file_name)

                    try:
                        # Download from S3
                        download_s3_file(bucket, s3_key, local_file)
                        print(f"Downloaded and uploading {file_name}...")

                        # Upload to HuggingFace
                        api.upload_file(
                            path_or_fileobj=local_file,
                            path_in_repo=f"data/{file_name}",
                            repo_id=repo_name,
                            repo_type="dataset",
                            token=token
                        )

                    except Exception as e:
                        print(f"Error uploading {s3_key}: {e}")
                        continue

        else:
            # Handle local path
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
    dataset_card = create_dataset_card(repo_name, dump_id, total_docs, total_tokens, stats)

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

    # Validate input directory/path
    if is_s3_path(args.input_dir):
        # For S3 paths, check if we can list files
        try:
            bucket, prefix = parse_s3_path(args.input_dir)
            jsonl_files = list_s3_files(bucket, prefix)
            if not jsonl_files:
                print(f"Error: No .jsonl.gz files found in {args.input_dir}")
                exit(1)
            print(f"Found {len(jsonl_files)} JSONL files in S3 to upload")
        except Exception as e:
            print(f"Error accessing S3 path {args.input_dir}: {e}")
            exit(1)
    else:
        # For local paths, check directory exists and has files
        if not os.path.exists(args.input_dir):
            print(f"Error: Input directory {args.input_dir} does not exist")
            exit(1)

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
        merge_files=args.merge_files,
        dump_id=args.dump_id
    )


if __name__ == "__main__":
    main()
