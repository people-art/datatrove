# FineWeb-Data Setup Guide

## Environment Configuration

To use FineWeb-Data with LLM-powered ontology generation, you need to set up your API keys.

### 1. Create .env file

Create a `.env` file in the project root directory:

```bash
# In the project root directory
touch .env
```

### 2. Add your API keys

Edit the `.env` file and add your OpenAI API key:

```env
# Required: OpenAI API key for LLM-powered ontology generation
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Optional: Hugging Face API key for model access
HUGGINGFACE_API_KEY=hf_your-huggingface-token-here

# Optional: AWS credentials for S3 access
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=us-east-1
```

### 3. How to get OpenAI API key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and paste it in your `.env` file

### 4. Test the setup

Run the test script to verify everything works:

```bash
cd finewebdata
python test_finewebdata.py
```

You should see successful ontology generation instead of fallback messages.

### 5. Usage Examples

Once configured, you can use FineWeb-Data like this:

```bash
# Generate education dataset with LLM enhancement
python finewebdata.py --domain education --mode slurm --use-llm-scoring --gpu

# Test ontology generation for any domain
python finewebdata.py --domain "artificial intelligence" --benchmark

# Run on local machine for testing
python finewebdata.py --domain environment --mode local
```

### 6. Troubleshooting

- **"LLM ontology generation failed"**: Check your OpenAI API key is correct and has credits
- **"Expecting value: line 1 column 1 (char 0)"**: API response format error, try again or check API key
- **Fallback mode works**: The system will use rule-based ontologies for common domains even without API keys

### 7. Security Notes

- Never commit `.env` files to version control
- The `.env` file is automatically ignored by git
- Keep your API keys secure and rotate them regularly
- Use environment-specific keys (dev/staging/prod)
