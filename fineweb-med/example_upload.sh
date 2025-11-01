#!/bin/bash

# FineWeb-Med HuggingFace Upload Example
# Replace the placeholders with your actual values

# === IMPORTANT: CONFIGURE THESE VALUES ===

# Your HuggingFace token (get from https://huggingface.co/settings/tokens)
# Make sure the token has "Write" permissions for dataset creation
HF_TOKEN="your_huggingface_token_here"

# Your HuggingFace username (NOT email, but your username)
# Find it at: https://huggingface.co/settings/profile
# It should be the part after https://huggingface.co/ in your profile URL
HF_USERNAME="your_actual_huggingface_username"

# Repository name - don't change this part
REPO_NAME="${HF_USERNAME}/fineweb-med"

# Input directory (relative to project root)
INPUT_DIR="data/fineweb-med/base_processing/output/CC-MAIN-2023-50"

# === END CONFIGURATION ===

echo "🚀 Starting FineWeb-Med dataset upload to HuggingFace Hub"
echo "👤 Username: $HF_USERNAME"
echo "📁 Repository: $REPO_NAME"
echo "📂 Input directory: $INPUT_DIR"
echo ""

# Validate configuration
if [ "$HF_TOKEN" = "your_huggingface_token_here" ]; then
    echo "❌ ERROR: Please set your actual HuggingFace token!"
    echo "   Get it from: https://huggingface.co/settings/tokens"
    echo "   Make sure to grant 'Write' permissions"
    exit 1
fi

if [ "$HF_USERNAME" = "your_actual_huggingface_username" ]; then
    echo "❌ ERROR: Please set your actual HuggingFace username!"
    echo "   Find it at: https://huggingface.co/settings/profile"
    echo "   It's the name shown in your profile URL"
    exit 1
fi

echo "✅ Configuration validated"
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
