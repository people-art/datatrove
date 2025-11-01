#!/bin/bash

# FineWeb-Med HuggingFace Upload Example
# This script reads HF_TOKEN and HF_USERNAME from .env file

set -e  # Exit on error

# Input directory (relative to project root)
INPUT_DIR="data/fineweb-med/base_processing/output/CC-MAIN-2023-50"

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "❌ ERROR: .env file not found in project root!"
    echo "   Please create .env file with HF_TOKEN and HF_USERNAME"
    echo "   Example:"
    echo "   HF_TOKEN=hf_your_token_here"
    echo "   HF_USERNAME=your_username_here"
    exit 1
fi

# Load environment variables from .env file
set -a
source "../.env"
set +a

echo "🚀 Starting FineWeb-Med dataset upload to HuggingFace Hub"

# Validate required environment variables
if [ -z "$HF_TOKEN" ]; then
    echo "❌ ERROR: HF_TOKEN not found in .env file!"
    echo "   Add to .env: HF_TOKEN=hf_your_token_here"
    echo "   Get token from: https://huggingface.co/settings/tokens"
    exit 1
fi

if [ -z "$HF_USERNAME" ]; then
    echo "❌ ERROR: HF_USERNAME not found in .env file!"
    echo "   Add to .env: HF_USERNAME=your_username_here"
    echo "   Find username at: https://huggingface.co/settings/profile"
    exit 1
fi

# Check for placeholder values
if [[ "$HF_TOKEN" == *"your"* ]] || [[ "$HF_TOKEN" == *"here"* ]]; then
    echo "❌ ERROR: HF_TOKEN appears to be a placeholder!"
    echo "   Please set your actual HuggingFace token in .env"
    exit 1
fi

if [[ "$HF_USERNAME" == *"your"* ]] || [[ "$HF_USERNAME" == *"here"* ]]; then
    echo "❌ ERROR: HF_USERNAME appears to be a placeholder!"
    echo "   Please set your actual HuggingFace username in .env"
    exit 1
fi

REPO_NAME="${HF_USERNAME}/fineweb-med"

echo "👤 Username: $HF_USERNAME"
echo "📁 Repository: $REPO_NAME"
echo "📂 Input directory: $INPUT_DIR"
echo "✅ Configuration validated from .env file"
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
