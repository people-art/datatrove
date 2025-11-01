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
    PerplexityFilter,
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

# Medical-specific filters - expanded with MeSH terms and medical terminology
MEDICAL_KEYWORDS = [
    # Basic medical terms
    "medical", "diagnosis", "treatment", "patient", "doctor", "symptom", "therapy",
    "prescription", "clinical", "healthcare", "medicine", "pharmaceutical",
    "hospital", "clinic", "nurse", "surgery", "disease", "disorder", "condition",
    "medication", "drug", "vaccine", "epidemic", "pandemic", "health", "wellness",

    # Medical specialties and roles
    "cardiology", "oncology", "neurology", "psychiatry", "dermatology", "radiology",
    "pathology", "pediatrics", "geriatrics", "gynecology", "urology", "ophthalmology",
    "orthopedics", "endocrinology", "gastroenterology", "nephrology", "pulmonology",
    "rheumatology", "hematology", "infectious", "emergency", "intensive care",

    # Medical procedures and interventions
    "biopsy", "chemotherapy", "radiotherapy", "surgical", "transplant", "dialysis",
    "ventilation", "resuscitation", "anesthesia", "endoscopy", "colonoscopy",
    "angiography", "echocardiogram", "mammography", "ct scan", "mri", "ultrasound",

    # Medical conditions and diseases (MeSH-inspired)
    "cancer", "tumor", "carcinoma", "sarcoma", "leukemia", "lymphoma", "myocardial",
    "infarction", "stroke", "diabetes", "hypertension", "asthma", "arthritis",
    "osteoporosis", "alzheimer", "dementia", "parkinson", "epilepsy", "migraine",
    "depression", "anxiety", "schizophrenia", "autism", "adhd",

    # Anatomical and physiological terms
    "cardiovascular", "respiratory", "gastrointestinal", "genitourinary", "musculoskeletal",
    "endocrine", "immune", "nervous", "circulatory", "digestive", "reproductive",

    # Medical research and evidence
    "randomized", "controlled trial", "meta-analysis", "systematic review", "cohort study",
    "case-control", "epidemiology", "pharmacokinetics", "pharmacodynamics", "toxicology",

    # Healthcare policy and economics
    "medicare", "medicaid", "health insurance", "reimbursement", "health policy",
    "public health", "epidemiology", "vaccination", "immunization", "screening",

    # Medical devices and technology
    "prosthesis", "implant", "stent", "pacemaker", "defibrillator", "catheter",
    "ventilator", "monitor", "infusion", "syringe", "scalpel",

    # Laboratory and diagnostic terms
    "blood test", "urine test", "biochemical", "histopathology", "microbiology",
    "serology", "immunoassay", "pcr", "sequencing", "genomics", "proteomics",

    # Pharmacological terms
    "dosage", "side effect", "adverse reaction", "contraindication", "interaction",
    "metabolism", "clearance", "half-life", "bioavailability", "therapeutic index"
]


def is_medical_content(text: str, keywords: list, threshold: int = 2) -> bool:
    """
    Enhanced medical content detection with multiple criteria:
    1. Contains multiple medical keywords
    2. Has medical context (not just casual mentions)
    3. Avoids false positives from generic health mentions
    """
    text_lower = text.lower()

    # Count medical keywords (require at least threshold for stronger filtering)
    keyword_count = sum(1 for keyword in keywords if keyword.lower() in text_lower)

    # Basic threshold: at least threshold medical keywords
    if keyword_count < threshold:
        return False

    # Additional checks to avoid false positives
    medical_context_indicators = [
        # Medical institutions and roles
        "hospital", "clinic", "doctor", "nurse", "physician", "surgeon", "patient",
        # Medical procedures and treatments
        "treatment", "therapy", "surgery", "diagnosis", "prescription", "medication",
        # Medical research and science
        "clinical trial", "randomized", "meta-analysis", "epidemiology", "pathology",
        # Medical conditions (more specific ones)
        "cancer", "diabetes", "hypertension", "asthma", "arthritis", "stroke", "infarction"
    ]

    context_count = sum(1 for indicator in medical_context_indicators if indicator in text_lower)

    # Require at least one strong medical context indicator
    return context_count >= 1 or keyword_count >= 3


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='FineWeb-Med: Medical dataset processing pipeline')

    parser.add_argument('--mode', choices=['local', 'slurm'],
                       default='local',
                       help='Execution mode: local or slurm cluster (default: local)')

    parser.add_argument('--cluster-name',
                       default='fineweb-med-slurm-cluster',
                       help='Slurm cluster name (only used in slurm mode)')

    parser.add_argument('--dumps', nargs='+', default=['CC-MAIN-2023-50'],
                       help='Common Crawl dumps to process (default: CC-MAIN-2023-50)')

    parser.add_argument('--dump', default='CC-MAIN-2023-50',
                       help='Single Common Crawl dump to process (for backward compatibility)')

    parser.add_argument('--output-bucket', default='fineweb-med',
                       help='S3 bucket name for output (default: fineweb-med)')

    parser.add_argument('--min-words', type=int, default=200,
                       help='Minimum word count for documents (default: 200)')

    parser.add_argument('--medical-threshold', type=int, default=2,
                       help='Minimum number of medical keywords required (default: 2)')

    parser.add_argument('--compression', choices=['gzip', 'none'], default='gzip',
                       help='Output compression format (default: gzip)')

    parser.add_argument('--skip-dedup', action='store_true',
                       help='Skip deduplication step (useful for testing)')

    return parser.parse_args()


def create_executor(mode, cluster_name, dumps, output_bucket, min_words=200,
                   medical_threshold=2, compression='gzip', skip_dedup=False):
    """Create the appropriate executor based on mode."""

    # Update global variables based on arguments
    global DUMP_TO_PROCESS, MAIN_OUTPUT_PATH, FILTERING_OUTPUT_PATH
    # Use the first dump as primary for backward compatibility, but support multiple
    DUMP_TO_PROCESS = dumps[0] if isinstance(dumps, list) else dumps
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
        # Enhanced medical content filter - more sophisticated filtering
        LambdaFilter(
            lambda doc: is_medical_content(doc.text, MEDICAL_KEYWORDS, medical_threshold),
            exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/3_non_medical/{DUMP_TO_PROCESS}")
        ),
        # Minimum length filter - medical documents should be substantial
        LambdaFilter(
            lambda doc: len(doc.text.split()) >= min_words,
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
        # Perplexity filter to ensure content quality (lower perplexity = better quality)
        PerplexityFilter(
            exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/9_perplexity/{DUMP_TO_PROCESS}")
        ),
        # PII removal is crucial for medical data - apply before final output
        PIIFormatter(),
        TokensCounter(),
        JsonlWriter(f"{FILTERING_OUTPUT_PATH}/output/{DUMP_TO_PROCESS}", compression=compression if compression != 'none' else None),
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

# Local testing with single dump
python fineweb-med-new.py --dump CC-MAIN-2023-40

# Local testing with multiple dumps
python fineweb-med-new.py --dumps CC-MAIN-2023-40 CC-MAIN-2023-50

# Slurm cluster production run (single dump)
python fineweb-med-new.py --mode slurm --cluster-name my-cluster --dump CC-MAIN-2023-50

# Slurm cluster production run (multiple dumps)
python fineweb-med-new.py --mode slurm --dumps CC-MAIN-2023-40 CC-MAIN-2023-50 CC-MAIN-2024-05

# Full command with all options
python fineweb-med-new.py --mode slurm --cluster-name fineweb-med-slurm-cluster --dumps CC-MAIN-2023-50 --output-bucket fineweb-med --min-words 200 --medical-threshold 2 --compression gzip
"""
if __name__ == '__main__':
    # Parse command line arguments
    args = parse_args()

    # Handle backward compatibility: use --dump if --dumps not specified
    dumps_to_process = args.dumps if hasattr(args, 'dumps') and args.dumps != ['CC-MAIN-2023-50'] else [args.dump]

    print(f"📊 Processing {len(dumps_to_process)} Common Crawl dumps: {dumps_to_process}")

    # For now, process dumps sequentially (can be parallelized later)
    for dump_id in dumps_to_process:
        print(f"\n🔄 Processing dump: {dump_id}")

        # Create executor based on mode
        main_processing_executor = create_executor(
            mode=args.mode,
            cluster_name=args.cluster_name,
            dumps=[dump_id],  # Pass as list for consistency
            output_bucket=args.output_bucket,
            min_words=args.min_words,
            medical_threshold=args.medical_threshold,
            compression=args.compression,
            skip_dedup=args.skip_dedup
        )

        # Launch the base processing pipeline for this dump
        main_processing_executor.run()

    # Only run deduplication in slurm mode (production)
    if args.mode == 'slurm':
        print("\n🔄 Starting deduplication pipeline...")

        # For deduplication, we need to process all dumps together
        # This would require modifying the deduplication logic to handle multiple inputs
        print("⚠️  Multi-dump deduplication not yet implemented. Processing individual dumps.")

        print("✅ Production processing completed!")
    else:
        print("✅ Local processing completed. Use --mode slurm for full production processing.")

