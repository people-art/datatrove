#!/usr/bin/env python3
"""
FineWeb-Data Dataset Statistics Generator

This script analyzes processed datasets and generates statistics and data cards.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from collections import Counter
import re

try:
    import boto3
    from botocore import UNSIGNED
    from botocore.client import Config
except ImportError:
    print("Missing boto3. Install with: pip install boto3")
    exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate FineWeb-Data dataset statistics')

    parser.add_argument('--input-dir', required=True,
                       help='Directory containing processed dataset files')

    parser.add_argument('--domain', help='Domain of the dataset')

    parser.add_argument('--output-file', default='dataset_stats.json',
                       help='Output file for statistics (JSON)')

    parser.add_argument('--generate-card', action='store_true',
                       help='Generate dataset card (README.md)')

    parser.add_argument('--max-files', type=int, default=100,
                       help='Maximum number of files to sample for stats')

    return parser.parse_args()


def get_files_from_s3(s3_path: str, max_files: int = 100) -> List[str]:
    """Get list of files from S3 directory."""
    if not s3_path.startswith('s3://'):
        return []

    path_parts = s3_path.replace('s3://', '').split('/')
    bucket = path_parts[0]
    prefix = '/'.join(path_parts[1:])

    s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))

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


def get_files_from_local(local_path: str, max_files: int = 100) -> List[str]:
    """Get list of files from local directory."""
    path = Path(local_path)
    if not path.exists():
        return []

    files = []
    for file_path in path.glob('**/*.jsonl.gz'):
        files.append(str(file_path))
        if len(files) >= max_files:
            break

    return files


def sample_documents(file_paths: List[str], max_docs: int = 10000) -> pd.DataFrame:
    """Sample documents from files for analysis."""
    documents = []
    docs_per_file = max(1, max_docs // len(file_paths))

    for file_path in file_paths:
        try:
            if file_path.startswith('s3://'):
                # Load from S3
                s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
                path_parts = file_path.replace('s3://', '').split('/')
                bucket = path_parts[0]
                key = '/'.join(path_parts[1:])

                obj = s3_client.get_object(Bucket=bucket, Key=key)
                content = obj['Body'].read().decode('utf-8')
                lines = content.strip().split('\n')
            else:
                # Load from local
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

            # Sample documents
            step = max(1, len(lines) // docs_per_file)
            for i in range(0, min(len(lines), docs_per_file * step), step):
                line = lines[i].strip()
                if line:
                    try:
                        doc = json.loads(line)
                        documents.append(doc)
                        if len(documents) >= max_docs:
                            break
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            print(f"Warning: Failed to process {file_path}: {e}")
            continue

        if len(documents) >= max_docs:
            break

    return pd.DataFrame(documents)


def analyze_text_quality(text: str) -> Dict[str, Any]:
    """Analyze text quality metrics."""
    if not text:
        return {'length': 0, 'sentences': 0, 'words': 0, 'quality_score': 0}

    # Basic metrics
    words = text.split()
    sentences = re.split(r'[.!?]+', text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    # Quality heuristics
    quality_score = 0

    # Length check
    if 50 <= len(words) <= 2000:
        quality_score += 1

    # Sentence structure
    if len(sentences) >= 3:
        quality_score += 1

    # Diversity (unique words ratio)
    if words:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio > 0.3:
            quality_score += 1

    return {
        'length': len(text),
        'sentences': len(sentences),
        'words': len(words),
        'quality_score': quality_score
    }


def generate_statistics(df: pd.DataFrame, domain: str = None) -> Dict[str, Any]:
    """Generate comprehensive dataset statistics."""
    if df.empty:
        return {'error': 'No data to analyze'}

    stats = {
        'dataset_info': {
            'total_documents': len(df),
            'domain': domain,
            'columns': list(df.columns)
        },

        'text_statistics': {},
        'quality_metrics': {},
        'content_analysis': {}
    }

    # Text statistics
    if 'text' in df.columns:
        texts = df['text'].dropna()

        text_lengths = []
        word_counts = []
        sentence_counts = []
        quality_scores = []

        for text in texts.sample(min(1000, len(texts))):  # Sample for efficiency
            analysis = analyze_text_quality(str(text))
            text_lengths.append(analysis['length'])
            word_counts.append(analysis['words'])
            sentence_counts.append(analysis['sentences'])
            quality_scores.append(analysis['quality_score'])

        stats['text_statistics'] = {
            'avg_text_length': sum(text_lengths) / len(text_lengths) if text_lengths else 0,
            'avg_word_count': sum(word_counts) / len(word_counts) if word_counts else 0,
            'avg_sentence_count': sum(sentence_counts) / len(sentence_counts) if sentence_counts else 0,
            'quality_score_distribution': dict(Counter(quality_scores))
        }

    # Quality metrics
    stats['quality_metrics'] = {
        'documents_with_text': len(df[df['text'].notna()]) if 'text' in df.columns else 0,
        'unique_urls': df['url'].nunique() if 'url' in df.columns else 0,
        'unique_dumps': df['dump'].nunique() if 'dump' in df.columns else 0
    }

    # Content analysis
    if domain and 'text' in df.columns:
        # Domain-specific analysis would go here
        # For now, just basic word frequency
        all_text = ' '.join(df['text'].dropna().astype(str).sample(min(100, len(df))))
        words = re.findall(r'\b\w+\b', all_text.lower())
        word_freq = Counter(words).most_common(20)

        stats['content_analysis'] = {
            'top_words': dict(word_freq),
            'domain_relevance_indicators': ['analysis pending']  # Placeholder
        }

    return stats


def generate_dataset_card(stats: Dict[str, Any], domain: str = None) -> str:
    """Generate a dataset card in markdown format."""
    domain_info = f" for {domain}" if domain else ""

    card = f"""---
license: apache-2.0
task_categories:
- text-generation
language:
- en
tags:
- fineweb-data
- common-crawl
- web-scraping{'
- ' + domain.replace(' ', '-').lower() if domain else ''}
---

# FineWeb-Data Dataset Statistics{domain_info}

## Overview

This dataset contains processed web content from Common Crawl, filtered for quality and domain relevance.

## Dataset Statistics

### Basic Information
- **Total Documents**: {stats.get('dataset_info', {}).get('total_documents', 'N/A')}
- **Domain**: {domain or 'General'}
- **Data Source**: Common Crawl

### Text Statistics
- **Average Text Length**: {stats.get('text_statistics', {}).get('avg_text_length', 0):.0f} characters
- **Average Word Count**: {stats.get('text_statistics', {}).get('avg_word_count', 0):.0f} words
- **Average Sentences**: {stats.get('text_statistics', {}).get('avg_sentence_count', 0):.1f} sentences

### Quality Metrics
- **Documents with Content**: {stats.get('quality_metrics', {}).get('documents_with_text', 0)}
- **Unique URLs**: {stats.get('quality_metrics', {}).get('unique_urls', 0)}
- **Unique Dumps**: {stats.get('quality_metrics', {}).get('unique_dumps', 0)}

### Quality Score Distribution
{chr(10).join([f"- Score {score}: {count} documents" for score, count in stats.get('text_statistics', {}).get('quality_score_distribution', {}).items()])}

## Processing Pipeline

1. **Domain Ontology Generation**: LLM-powered ontology creation
2. **Content Filtering**: Multi-layer quality and relevance filtering
3. **PII Redaction**: Privacy protection
4. **Deduplication**: MinHash-based duplicate removal

## Usage

```python
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("your-username/fineweb-data{domain_info.replace(' ', '-').lower()}")

# Access documents
for doc in dataset['train']:
    print(doc['text'])
```
"""

    return card


def main():
    args = parse_args()

    print(f"📊 Analyzing FineWeb-Data{' for ' + args.domain if args.domain else ''}")

    # Get file list
    if args.input_dir.startswith('s3://'):
        files = get_files_from_s3(args.input_dir, args.max_files)
    else:
        files = get_files_from_local(args.input_dir, args.max_files)

    if not files:
        print(f"❌ No files found in {args.input_dir}")
        return

    print(f"📁 Found {len(files)} files for analysis")

    # Sample documents
    print("🔍 Sampling documents for analysis...")
    df = sample_documents(files, 5000)  # Sample 5000 docs for stats

    if df.empty:
        print("❌ No valid documents found")
        return

    print(f"📈 Analyzing {len(df)} documents...")

    # Generate statistics
    stats = generate_statistics(df, args.domain)

    # Save statistics
    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"✅ Statistics saved to {args.output_file}")

    # Generate dataset card if requested
    if args.generate_card:
        card_content = generate_dataset_card(stats, args.domain)
        card_file = args.output_file.replace('.json', '_card.md')

        with open(card_file, 'w', encoding='utf-8') as f:
            f.write(card_content)

        print(f"📝 Dataset card saved to {card_file}")

    # Print summary
    print("\n📊 Summary:")
    print(f"  - Total documents: {stats['dataset_info']['total_documents']:,}")
    print(f"  - Avg text length: {stats['text_statistics'].get('avg_text_length', 0):.0f} chars")
    print(f"  - Avg word count: {stats['text_statistics'].get('avg_word_count', 0):.0f} words")
    print(f"  - Quality scores: {stats['text_statistics'].get('quality_score_distribution', {})}")


if __name__ == '__main__':
    main()
