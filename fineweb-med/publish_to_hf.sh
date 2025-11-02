#!/bin/bash

# FineWeb-Med HuggingFace Upload Example
# This script reads HF_TOKEN and HF_USERNAME from .env file
#
# Usage:
#   ./publish_to_hf.sh                    # Interactive mode
#   ./publish_to_hf.sh --latest          # Upload latest dump non-interactively
#   ./publish_to_hf.sh --dump CC-MAIN-2024-18  # Upload specific dump
#   ./publish_to_hf.sh --all             # Upload all available dumps
#   ./publish_to_hf.sh --name my-dataset # Upload to custom dataset name

set -e  # Exit on error

# Parse command line arguments
NON_INTERACTIVE=false
SELECT_MODE="interactive"
REPO_BASE_NAME="fineweb-med"  # Default repository base name

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "FineWeb-Med HuggingFace Upload Script"
            echo ""
            echo "Usage:"
            echo "  $0                           # Interactive mode"
            echo "  $0 --latest                 # Upload latest dump non-interactively"
            echo "  $0 --dump CC-MAIN-2024-18   # Upload specific dump"
            echo "  $0 --all                    # Upload all available dumps"
            echo "  $0 --name my-dataset        # Set custom dataset name (default: fineweb-med)"
            echo "  $0 --help                   # Show this help"
            echo ""
            echo "The script automatically scans s3://fineweb-med/base_processing/output/"
            echo "for available CC-MAIN-* dumps and allows you to select which ones to upload."
            echo ""
            echo "Requirements:"
            echo "  - .env file in project root with HF_TOKEN and HF_USERNAME"
            echo "  - AWS credentials (optional, for authenticated S3 access)"
            exit 0
            ;;
        --latest)
            NON_INTERACTIVE=true
            SELECT_MODE="latest"
            shift
            ;;
        --all)
            NON_INTERACTIVE=true
            SELECT_MODE="all"
            shift
            ;;
        --dump)
            NON_INTERACTIVE=true
            SELECT_MODE="specific"
            SPECIFIC_DUMP="$2"
            shift 2
            ;;
        --name)
            REPO_BASE_NAME="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--latest|--all|--dump DUMP_ID|--name NAME|--help]"
            exit 1
            ;;
    esac
done

# Base directory (S3 path for processed data)
BASE_DIR="s3://fineweb-med/base_processing/output"

# Function to list available dumps in S3
list_available_dumps() {
    # Use AWS CLI to list objects with CC-MAIN prefix
    if command -v aws &> /dev/null; then
        # Try to list with AWS CLI
        dumps=$(aws s3 ls "$BASE_DIR/" 2>/dev/null | grep "CC-MAIN-" | awk '{print $2}' | sed 's/\///' | sort -r)
    else
        # Fallback: try to use boto3 via Python if AWS CLI not available
        dumps=$(python3 -c "
import boto3
from botocore import UNSIGNED
from botocore.client import Config
import os

# Try with credentials first
try:
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket='fineweb-med', Prefix='base_processing/output/')
    dumps = []
    if 'Contents' in response:
        for obj in response['Contents']:
            key = obj['Key']
            if 'base_processing/output/' in key and 'CC-MAIN-' in key:
                dump = key.split('/')[2]  # Extract dump ID from path
                if dump.startswith('CC-MAIN-') and dump not in dumps:
                    dumps.append(dump)
    dumps.sort(reverse=True)
    print('\n'.join(dumps))
except:
    print('CC-MAIN-2023-50\nCC-MAIN-2024-18', file=__import__('sys').stderr)
" 2>/dev/null)
    fi

    # Return dumps or exit with error
    if [ -z "$dumps" ]; then
        return 1  # Return error code instead of exit
    fi

    echo "$dumps"
}

# Function for dump selection (interactive or non-interactive)
select_dump() {
    dumps=$1

    if [ "$NON_INTERACTIVE" = true ]; then
        case $SELECT_MODE in
            latest)
                selected_dump=$(echo "$dumps" | head -n 1)
                echo "🤖 Non-interactive mode: Using latest dump: $selected_dump" >&2
                echo "$selected_dump"
                return
                ;;
            all)
                echo "🤖 Non-interactive mode: Uploading all dumps sequentially" >&2
                echo "$dumps"
                return
                ;;
            specific)
                if echo "$dumps" | grep -q "^$SPECIFIC_DUMP$"; then
                    echo "🤖 Non-interactive mode: Using specified dump: $SPECIFIC_DUMP" >&2
                    echo "$SPECIFIC_DUMP"
                    return
                else
                    echo "❌ Specified dump '$SPECIFIC_DUMP' not found in available dumps:" >&2
                    echo "$dumps" >&2
                    exit 1
                fi
                ;;
        esac
    else
        # Interactive mode
        echo "" >&2
        echo "📊 Available dumps:" >&2
        echo "$dumps" | nl -v 1 >&2

        echo "" >&2
        echo "🔍 Selection options:" >&2
        echo "  'latest' - Use the most recent dump (default)" >&2
        echo "  'all' - Upload all dumps (one by one)" >&2
        echo "  number - Select specific dump by number" >&2
        echo "" >&2

        while true; do
            read -p "Enter your selection [latest]: " choice >&2
            choice=${choice:-latest}

            case $choice in
                latest)
                    selected_dump=$(echo "$dumps" | head -n 1)
                    echo "📦 Selected latest dump: $selected_dump" >&2
                    echo "$selected_dump"
                    return
                    ;;
                all)
                    echo "📦 Will upload all dumps sequentially" >&2
                    echo "$dumps"
                    return
                    ;;
                [0-9]*)
                    dump_count=$(echo "$dumps" | wc -l)
                    if [ "$choice" -ge 1 ] && [ "$choice" -le "$dump_count" ]; then
                        selected_dump=$(echo "$dumps" | sed -n "${choice}p")
                        echo "📦 Selected dump: $selected_dump" >&2
                        echo "$selected_dump"
                        return
                    else
                        echo "❌ Invalid number. Please enter a number between 1 and $dump_count" >&2
                    fi
                    ;;
                *)
                    echo "❌ Invalid choice. Please enter 'latest', 'all', or a number" >&2
                    ;;
            esac
        done
    fi
}

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

REPO_NAME="${HF_USERNAME}/${REPO_BASE_NAME}"

echo "👤 Username: $HF_USERNAME"
echo "📁 Repository: $REPO_NAME"
echo "📂 Base directory: $BASE_DIR"
echo "✅ Configuration validated from .env file"
echo ""

# List and select available dumps
echo "🔍 Scanning for available dumps in $BASE_DIR..."
available_dumps=$(list_available_dumps)
if [ $? -ne 0 ]; then
    echo "❌ No dumps found in $BASE_DIR"
    echo "   Make sure the processing pipeline has completed successfully."
    exit 1
fi
echo "📊 Found $(echo "$available_dumps" | wc -l) available dumps"

selected_dumps=$(select_dump "$available_dumps")

# Process selected dumps
dump_count=$(echo "$selected_dumps" | wc -l)
current_dump=1

for dump_id in $selected_dumps; do
    echo ""
    echo "🚀 Processing dump $current_dump/$dump_count: $dump_id"

    INPUT_DIR="$BASE_DIR/$dump_id"
    REPO_SUFFIX=$(echo "$dump_id" | tr '[:upper:]' '[:lower:]' | sed 's/cc-main-/cc/')

    # For multiple dumps, we merge them into a single repository
    # Only use suffix for single dump selection from multiple available dumps
    if [ "$dump_count" -eq 1 ] && [ "$selected_dumps" != "$available_dumps" ]; then
        # Single specific dump selected, use suffix to distinguish
        CURRENT_REPO_NAME="${HF_USERNAME}/${REPO_BASE_NAME}-${REPO_SUFFIX}"
    else
        # Multiple dumps (merge into one) or 'latest' or 'all', use base name
        CURRENT_REPO_NAME="$REPO_NAME"
    fi

    echo "📂 Input directory: $INPUT_DIR"
    echo "📦 Target repository: $CURRENT_REPO_NAME"

    # Run the upload script for this dump
    python upload_to_huggingface.py \
        --input-dir "$INPUT_DIR" \
        --repo-name "$CURRENT_REPO_NAME" \
        --token "$HF_TOKEN" \
        --dump-id "$dump_id"

    echo "✅ Completed upload for dump: $dump_id"

    # Add delay between uploads to avoid rate limiting
    if [ "$current_dump" -lt "$dump_count" ]; then
        echo "⏳ Waiting 30 seconds before next upload to avoid rate limiting..."
        sleep 30
    fi

    echo ""
    current_dump=$((current_dump + 1))
done

echo ""
echo "✅ All uploads completed!"

# Show links to uploaded repositories
dump_count=$(echo "$selected_dumps" | wc -l)
if [ "$dump_count" -gt 1 ]; then
    echo "🌐 Uploaded datasets:"
    for dump_id in $selected_dumps; do
        REPO_SUFFIX=$(echo "$dump_id" | tr '[:upper:]' '[:lower:]' | sed 's/cc-main-/cc/')
        CURRENT_REPO_NAME="${HF_USERNAME}/${REPO_BASE_NAME}-${REPO_SUFFIX}"
        echo "   📦 $dump_id → https://huggingface.co/datasets/$CURRENT_REPO_NAME"
    done
else
    echo "🌐 View your dataset at: https://huggingface.co/datasets/$REPO_NAME"
fi
