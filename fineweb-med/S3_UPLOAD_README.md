# S3 Dataset Upload Support

The upload script now supports reading datasets directly from S3 buckets:

## Usage Examples

### From S3 Bucket (Recommended)
```bash
python upload_to_huggingface.py     --input-dir s3://your-bucket/base_processing/output/CC-MAIN-2024-18     --repo-name your-username/fineweb-med     --token your_hf_token
```

### From Local Directory
```bash
python upload_to_huggingface.py     --input-dir /path/to/local/data     --repo-name your-username/fineweb-med     --token your_hf_token
```

## Requirements

Add boto3 to your dependencies:
```bash
pip install boto3
```

## S3 Bucket Access

- Public buckets: Anonymous access (no credentials needed)
- Private buckets: Configure AWS credentials in environment or ~/.aws/credentials

The script automatically detects S3 vs local paths and handles them appropriately.
