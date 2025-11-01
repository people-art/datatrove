# FineWeb-Med S3 Bucket Access Setup

## Problem
The upload script is failing with "Access Denied" when trying to access the `fineweb-med` S3 bucket.

## Root Cause
The bucket has S3 Block Public Access enabled, which prevents applying public bucket policies.

## Solutions

### Option 1: Attach IAM Policy to User (Recommended)

1. **Create IAM Policy** (if not already done):
   ```bash
   aws iam create-policy \
     --policy-name FineWebMedS3Access \
     --policy-document file://../fineweb_med_iam_policy.json
   ```

2. **Attach Policy to User**:
   ```bash
   aws iam attach-user-policy \
     --user-name YOUR_USER_NAME \
     --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/FineWebMedS3Access
   ```

### Option 2: Use Pre-signed URLs (Alternative)

Modify the upload script to generate pre-signed URLs for temporary access.

### Option 3: Temporary Disable Block Public Access (Not Recommended)

⚠️ **Warning**: This makes the bucket publicly accessible!

```bash
# Temporarily disable block public access
aws s3api put-public-access-block --bucket fineweb-med --public-access-block-configuration '{}'

# Apply public read policy
aws s3api put-bucket-policy --bucket fineweb-med --policy file://../s3_bucket_policy.json

# Re-enable block public access (IMPORTANT!)
aws s3api put-public-access-block --bucket fineweb-med --public-access-block-configuration '{
    "BlockPublicAcls": true,
    "IgnorePublicAcls": true,
    "BlockPublicPolicy": true,
    "RestrictPublicBuckets": true
}'
```

## Current Status

The bucket exists but access is restricted. You need to:
1. Apply the IAM policy to your user, OR
2. Temporarily disable Block Public Access to apply a public policy, OR  
3. Use a different authentication method

## Testing Access

After applying permissions, test with:
```bash
python upload_to_huggingface.py --input-dir s3://fineweb-med/base_processing/output/CC-MAIN-2024-18 --repo-name test/test --token dummy --dump-id test
```
