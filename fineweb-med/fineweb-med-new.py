"""
FineWeb-Med: Medical-focused dataset processing pipeline based on FineWeb methodology
"""

import os
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure anonymous access for Common Crawl (public bucket)
os.environ['AWS_ACCESS_KEY_ID'] = ''  # Clear credentials for anonymous access
os.environ['AWS_SECRET_ACCESS_KEY'] = ''  # Clear credentials for anonymous access
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

from datatrove.executor.local import LocalPipelineExecutor
from datatrove.executor.slurm import SlurmPipelineExecutor
from datatrove.pipeline.dedup import MinhashDedupCluster, MinhashDedupFilter, MinhashDedupSignature
from datatrove.pipeline.dedup.minhash import MinhashConfig, MinhashDedupBuckets
from datatrove.pipeline.extractors import Trafilatura
from datatrove.pipeline.filters import (
    C4QualityFilter,
    FineWebQualityFilter,
    GopherQualityFilter,
    GopherRepetitionFilter,
    LanguageFilter,
    LambdaFilter,
    URLFilter,
)
from datatrove.pipeline.formatters import PIIFormatter
from datatrove.pipeline.readers import JsonlReader, WarcReader
from datatrove.pipeline.tokens import TokensCounter
from datatrove.pipeline.writers.jsonl import JsonlWriter
from datatrove.utils.hashing import HashConfig


"""
Medical dataset processing pipeline based on FineWeb methodology
"""
DUMP_TO_PROCESS = "CC-MAIN-2023-50"  # example dump

MAIN_OUTPUT_PATH = "s3://fineweb-med"  # S3 bucket for production
FILTERING_OUTPUT_PATH = f"{MAIN_OUTPUT_PATH}/base_processing"

# Medical-specific filters
MEDICAL_KEYWORDS = [
    "medical", "diagnosis", "treatment", "patient", "doctor", "symptom", "therapy",
    "prescription", "clinical", "healthcare", "medicine", "pharmaceutical",
    "hospital", "clinic", "nurse", "surgery", "disease", "disorder", "condition",
    "medication", "drug", "vaccine", "epidemic", "pandemic", "health", "wellness"
]


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='FineWeb-Med: Medical dataset processing pipeline')

    parser.add_argument('--mode', choices=['local', 'slurm'],
                       default='local',
                       help='Execution mode: local or slurm cluster (default: local)')

    parser.add_argument('--cluster-name',
                       default='fineweb-med-slurm-cluster',
                       help='Slurm cluster name (only used in slurm mode)')

    parser.add_argument('--dump', default='CC-MAIN-2023-50',
                       help='Common Crawl dump to process (default: CC-MAIN-2023-50)')

    parser.add_argument('--output-bucket', default='fineweb-med',
                       help='S3 bucket name for output (default: fineweb-med)')

    return parser.parse_args()


def create_executor(mode, cluster_name, dump, output_bucket):
    """Create the appropriate executor based on mode."""

    # Update global variables based on arguments
    global DUMP_TO_PROCESS, MAIN_OUTPUT_PATH, FILTERING_OUTPUT_PATH
    DUMP_TO_PROCESS = dump
    MAIN_OUTPUT_PATH = f"s3://{output_bucket}"
    FILTERING_OUTPUT_PATH = f"{MAIN_OUTPUT_PATH}/base_processing"

    pipeline = [
        WarcReader(
            data_folder=f"s3://commoncrawl/crawl-data/{DUMP_TO_PROCESS}/segments/",
            glob_pattern="*/warc/*",  # we want the warc files
            default_metadata={"dump": DUMP_TO_PROCESS, "dataset": "fineweb-med"},
        ),
        URLFilter(exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/1_url/{DUMP_TO_PROCESS}")),
        Trafilatura(favour_precision=True, timeout=2),  # Slightly longer timeout for medical content
        LanguageFilter(
            exclusion_writer=JsonlWriter(
                f"{FILTERING_OUTPUT_PATH}/2_non_english/",
                output_filename="${language}/" + DUMP_TO_PROCESS + "/${rank}.jsonl.gz",
            )
        ),
        # Medical content filter - keep only documents containing medical keywords
        LambdaFilter(
            lambda doc: any(keyword.lower() in doc.text.lower() for keyword in MEDICAL_KEYWORDS),
            exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/3_non_medical/{DUMP_TO_PROCESS}")
        ),
        # Minimum length filter - medical documents should be substantial
        LambdaFilter(
            lambda doc: len(doc.text.split()) >= 200,
            exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/4_too_short/{DUMP_TO_PROCESS}")
        ),
        GopherRepetitionFilter(
            exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/5_gopher_rep/{DUMP_TO_PROCESS}")
        ),
        GopherQualityFilter(
            exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/6_gopher_qual/{DUMP_TO_PROCESS}")
        ),
        C4QualityFilter(
            filter_no_terminal_punct=False,
            exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/7_c4/{DUMP_TO_PROCESS}"),
        ),
        FineWebQualityFilter(
            exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/8_fineweb_qual/{DUMP_TO_PROCESS}")
        ),
        JsonlWriter(f"{FILTERING_OUTPUT_PATH}/output/{DUMP_TO_PROCESS}"),
    ]

    if mode == 'local':
        # Local mode with limited processing for testing
        print("🔧 Running in LOCAL mode")
        print(f"📁 Processing dump: {DUMP_TO_PROCESS}")
        print("⚠️  Limited to 100 documents per task for testing")

        pipeline[0] = WarcReader(
            data_folder=f"s3://commoncrawl/crawl-data/{DUMP_TO_PROCESS}/segments/",
            glob_pattern="*/warc/*",
            default_metadata={"dump": DUMP_TO_PROCESS, "dataset": "fineweb-med"},
            limit=100,  # Limit for local testing
        )

        executor = LocalPipelineExecutor(
            pipeline=pipeline,
            logging_dir=f"logs/base_processing/{DUMP_TO_PROCESS}",
            tasks=4,  # Fewer tasks for local testing
            workers=2,  # Local workers
        )

    else:  # slurm mode
        print("🚀 Running in SLURM mode")
        print(f"📁 Processing dump: {DUMP_TO_PROCESS}")
        print(f"🏗️  Cluster: {cluster_name}")
        print(f"💾 Output bucket: {output_bucket}")

        executor = SlurmPipelineExecutor(
            job_name=f"fineweb_med_{DUMP_TO_PROCESS}",
            pipeline=pipeline,
            tasks=4000,  # Full scale processing
            time="15:00:00",
            logging_dir=f"{MAIN_OUTPUT_PATH}/logs/base_processing/{DUMP_TO_PROCESS}",
            slurm_logs_folder=f"logs/base_processing/{DUMP_TO_PROCESS}/slurm_logs",
            randomize_start_duration=180,
            mem_per_cpu_gb=3,
            partition="hopper-cpu",
        )

    return executor



"""
Command Line Usage:

# Local testing (default)
python fineweb-med-new.py

# Local testing with custom dump
python fineweb-med-new.py --dump CC-MAIN-2023-40

# Slurm cluster production run
python fineweb-med-new.py --mode slurm --cluster-name my-cluster --output-bucket my-bucket

# Full command with all options
python fineweb-med-new.py --mode slurm --cluster-name fineweb-med-slurm-cluster --dump CC-MAIN-2023-50 --output-bucket fineweb-med
"""
if __name__ == '__main__':
    # Parse command line arguments
    args = parse_args()

    # Create executor based on mode
    main_processing_executor = create_executor(
        mode=args.mode,
        cluster_name=args.cluster_name,
        dump=args.dump,
        output_bucket=args.output_bucket
    )

    # Launch the base processing pipeline
    main_processing_executor.run()

    # Only run deduplication in slurm mode (production)
    if args.mode == 'slurm':
        print("\n🔄 Starting deduplication pipeline...")

        # Medical content may have more specific terminology, so we adjust minhash config
        minhash_config = MinhashConfig(
            hash_config=HashConfig(
                hash_fc="sha1",
                precision=64,
            ),
            num_buckets=10,  # Fewer buckets for medical dataset
            hashes_per_bucket=8,
            n_grams=5,  # 5-grams might be good for medical terminology
        )

        S3_MINHASH_BASE_PATH = f"{MAIN_OUTPUT_PATH}/minhash"
        S3_LOGS_FOLDER = f"{MAIN_OUTPUT_PATH}/logs/minhash"
        LOCAL_LOGS_FOLDER = "logs/minhash"

        TOTAL_TASKS = 500  # Fewer tasks for medical dataset

        # Input reader for deduplication
        INPUT_READER = JsonlReader(
            f"{FILTERING_OUTPUT_PATH}/output/{DUMP_TO_PROCESS}"
        )

        # Stage 1: Compute minhash signatures
        stage1 = SlurmPipelineExecutor(
            job_name=f"mh1_med_{DUMP_TO_PROCESS}",
            pipeline=[
                INPUT_READER,
                MinhashDedupSignature(
                    output_folder=f"{S3_MINHASH_BASE_PATH}/{DUMP_TO_PROCESS}/signatures", config=minhash_config
                ),
            ],
            tasks=TOTAL_TASKS,
            time="8:00:00",  # Longer time for medical content
            partition="hopper-cpu",
            logging_dir=f"{S3_LOGS_FOLDER}/signatures",
            slurm_logs_folder=f"{LOCAL_LOGS_FOLDER}/signatures/slurm_logs",
            randomize_start_duration=180,
            mem_per_cpu_gb=3,
            depends=main_processing_executor,
        )

        # Stage 2: Create buckets
        stage2 = SlurmPipelineExecutor(
            job_name=f"mh2_med_{DUMP_TO_PROCESS}",
            pipeline=[
                MinhashDedupBuckets(
                    input_folder=f"{S3_MINHASH_BASE_PATH}/{DUMP_TO_PROCESS}/signatures",
                    output_folder=f"{S3_MINHASH_BASE_PATH}/{DUMP_TO_PROCESS}/buckets",
                    config=MinhashConfig(hash_config=minhash_config.hash_config),
                ),
            ],
            tasks=minhash_config.num_buckets * 25,  # Fewer workers per bucket
            randomize_start_duration=180,
            logging_dir=f"{S3_LOGS_FOLDER}/buckets",
            partition="hopper-cpu",
            time="04:00:00",
            mem_per_cpu_gb=4,
            cpus_per_task=2,
            depends=stage1,
        )

        # Stage 3: Clustering
        stage3 = SlurmPipelineExecutor(
            job_name=f"mh3_med_{DUMP_TO_PROCESS}",
            pipeline=[
                MinhashDedupCluster(
                    input_folder=f"{S3_MINHASH_BASE_PATH}/{DUMP_TO_PROCESS}/buckets",
                    output_folder=f"{S3_MINHASH_BASE_PATH}/{DUMP_TO_PROCESS}/remove_ids",
                    config=minhash_config,
                ),
            ],
            tasks=1,
            logging_dir=f"{S3_LOGS_FOLDER}/clustering",
            partition="hopper-cpu",
            time="20:00:00",  # Adjusted time for medical dataset size
            mem_per_cpu_gb=20,  # Adjusted memory
            cpus_per_task=6,
            depends=stage2,
        )

        # Stage 4: Final filtering and output
        stage4 = SlurmPipelineExecutor(
            job_name=f"mh4_med_{DUMP_TO_PROCESS}",
            pipeline=[
                INPUT_READER,
                TokensCounter(),
                MinhashDedupFilter(input_folder=f"{S3_MINHASH_BASE_PATH}/{DUMP_TO_PROCESS}/remove_ids"),
                # PII removal is crucial for medical data
                PIIFormatter(),
                JsonlWriter(
                    f"{S3_MINHASH_BASE_PATH}/{DUMP_TO_PROCESS}/deduped_output",
                    compression="gzip"
                ),
            ],
            tasks=TOTAL_TASKS,
            logging_dir=f"{S3_LOGS_FOLDER}/filtering",
            partition="hopper-cpu",
            time="8:00:00",
            mem_per_cpu_gb=4,
            depends=stage3,
        )

        # Launch the deduplication pipeline
        stage4.run()

        print("✅ Production processing completed with deduplication!")
    else:
        print("✅ Local processing completed. Use --mode slurm for full production processing with deduplication.")
