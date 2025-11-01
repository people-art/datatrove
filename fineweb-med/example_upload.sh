#!/bin/bash

# FineWeb-Med HuggingFace Upload Example
# Replace the placeholders with your actual values

# Your HuggingFace token (get from https://huggingface.co/settings/tokens)
HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Your HuggingFace username
HF_USERNAME="your-username"

# Repository name
REPO_NAME="${HF_USERNAME}/fineweb-med"

# Input directory (relative to project root)
INPUT_DIR="data/fineweb-med/base_processing/output/CC-MAIN-2023-50"

echo "🚀 Starting FineWeb-Med dataset upload to HuggingFace Hub"
echo "📁 Repository: $REPO_NAME"
echo "📂 Input directory: $INPUT_DIR"
echo ""

# Run the upload script
python upload_to_huggingface.py \
    --input-dir "../$INPUT_DIR" \
    --repo-name "$REPO_NAME" \
    --token "$HF_TOKEN" \
    --dump-id "CC-MAIN-2023-50"

echo ""
echo "✅ Upload completed!"
echo "🌐 View your dataset at: https://huggingface.co/datasets/$REPO_NAME"
