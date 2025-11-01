import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure anonymous access for Common Crawl (public bucket)
os.environ['AWS_ACCESS_KEY_ID'] = ''  # Clear credentials for anonymous access
os.environ['AWS_SECRET_ACCESS_KEY'] = ''  # Clear credentials for anonymous access
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

from datatrove.pipeline.readers import WarcReader
from datatrove.pipeline.extractors import Trafilatura
from datatrove.pipeline.filters import LanguageFilter, RegexFilter, LambdaFilter
# from datatrove.pipeline.dedup import SentenceDedupFilter  # Commented out - deduplication requires complex setup
from datatrove.pipeline.tokens import TokensCounter
from datatrove.pipeline.writers import JsonlWriter
from datatrove.executor import LocalPipelineExecutor

pipeline = [
    WarcReader(data_folder="s3://commoncrawl/crawl-data/CC-MAIN-2023-50/segments/", glob_pattern="*/warc/*"),
    Trafilatura(),
    LanguageFilter(languages=["en"]),
    LambdaFilter(lambda doc: any(keyword.lower() in doc.text.lower() for keyword in ["medical", "diagnosis", "treatment", "patient", "doctor", "symptom", "therapy", "prescription", "clinical", "healthcare"])),
    LambdaFilter(lambda doc: len(doc.text.split()) >= 200),
    TokensCounter(),
    JsonlWriter(output_folder="s3://fineweb-med/datasets/", compression="gzip", output_filename="part-${rank}.jsonl.gz")
]

if __name__ == '__main__':
    executor = LocalPipelineExecutor(pipeline=pipeline, logging_dir="logs/fineweb_med", tasks=200, workers=20, skip_completed=True)
    executor.run()