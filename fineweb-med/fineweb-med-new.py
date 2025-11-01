"""
FineWeb-Med: Medical-focused dataset processing pipeline based on FineWeb methodology
"""

import os
import argparse
from dotenv import load_dotenv
import requests
from typing import List, Optional

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
    UnigramLogProbFilter,
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


def get_available_dumps(year: Optional[int] = None) -> List[str]:
    """
    Get available Common Crawl dumps for a specific year or all recent dumps.
    This function attempts to fetch from Common Crawl website or uses fallback known dumps.
    """
    try:
        # Try to fetch from Common Crawl website
        response = requests.get('https://commoncrawl.org/the-data/get-started/', timeout=10)
        if response.status_code == 200:
            # Simple regex to extract CC-MAIN patterns
            import re
            cc_main_pattern = r'CC-MAIN-\d{4}-\d{2}'
            dumps = re.findall(cc_main_pattern, response.text)
            dumps = list(set(dumps))  # Remove duplicates
            dumps.sort(reverse=True)  # Most recent first
        else:
            dumps = []
    except Exception:
        dumps = []

    # Fallback: known recent dumps (update as needed)
    fallback_dumps = [
        'CC-MAIN-2024-51', 'CC-MAIN-2024-50', 'CC-MAIN-2024-49', 'CC-MAIN-2024-46',
        'CC-MAIN-2024-42', 'CC-MAIN-2024-38', 'CC-MAIN-2024-33', 'CC-MAIN-2024-30',
        'CC-MAIN-2024-26', 'CC-MAIN-2024-22', 'CC-MAIN-2024-18', 'CC-MAIN-2024-15',
        'CC-MAIN-2024-10', 'CC-MAIN-2023-50', 'CC-MAIN-2023-40', 'CC-MAIN-2023-23',
        'CC-MAIN-2023-06', 'CC-MAIN-2022-49', 'CC-MAIN-2022-40', 'CC-MAIN-2022-33'
    ]

    if not dumps:
        dumps = fallback_dumps

    # Filter by year if specified
    if year:
        year_str = str(year)
        dumps = [d for d in dumps if d.split('-')[2] == year_str]

    return dumps


def select_dumps_interactive(available_dumps: List[str]) -> List[str]:
    """
    Interactive selection of dumps from available options.
    """
    print(f"\n📊 Found {len(available_dumps)} available Common Crawl dumps:")
    for i, dump in enumerate(available_dumps, 1):
        print(f"  {i:2d}. {dump}")

    print("\n🔍 Selection options:")
    print("  'all' - Select all dumps")
    print("  '1,3,5' - Select specific dumps by number")
    print("  '1-5' - Select range of dumps")
    print("  'latest' - Select the most recent dump")

    while True:
        choice = input("\nEnter your selection: ").strip().lower()

        if choice == 'all':
            return available_dumps
        elif choice == 'latest':
            return [available_dumps[0]] if available_dumps else []
        elif ',' in choice:
            # Handle comma-separated list
            try:
                indices = []
                for part in choice.split(','):
                    if '-' in part:
                        # Handle range
                        start, end = map(int, part.split('-'))
                        indices.extend(range(start-1, end))
                    else:
                        indices.append(int(part)-1)
                return [available_dumps[i] for i in indices if 0 <= i < len(available_dumps)]
            except (ValueError, IndexError):
                print("❌ Invalid selection. Please try again.")
                continue
        elif '-' in choice and ',' not in choice:
            # Handle range
            try:
                start, end = map(int, choice.split('-'))
                indices = list(range(start-1, end))
                return [available_dumps[i] for i in indices if 0 <= i < len(available_dumps)]
            except (ValueError, IndexError):
                print("❌ Invalid range. Please try again.")
                continue
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(available_dumps):
                    return [available_dumps[index]]
                else:
                    print("❌ Invalid number. Please try again.")
                    continue
            except ValueError:
                print("❌ Invalid input. Please try again.")
                continue


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

    parser.add_argument('--year', type=int,
                       help='Year to process (will show available dumps for that year)')

    parser.add_argument('--dumps', nargs='+',
                       help='Specific Common Crawl dumps to process (alternative to --year)')

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

    parser.add_argument('--non-interactive', action='store_true',
                       help='Skip interactive dump selection (use latest dump)')

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
        # Unigram log probability filter to ensure content quality (higher probability = better quality)
        UnigramLogProbFilter(
            exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/9_unigram_prob/{DUMP_TO_PROCESS}")
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

# Interactive mode - select from available dumps (default)
python fineweb-med-new.py

# Process dumps from a specific year (interactive selection)
python fineweb-med-new.py --year 2024

# Process specific dumps directly
python fineweb-med-new.py --dumps CC-MAIN-2023-40 CC-MAIN-2023-50

# Non-interactive mode (use latest available dump)
python fineweb-med-new.py --year 2024 --non-interactive

# Slurm cluster production run
python fineweb-med-new.py --mode slurm --year 2024

# Full command with all options
python fineweb-med-new.py --mode slurm --year 2024 --output-bucket fineweb-med --min-words 200 --medical-threshold 2 --compression gzip --non-interactive

Selection Options:
  'all' - Select all available dumps
  '1,3,5' - Select specific dumps by number
  '1-5' - Select range of dumps
  'latest' - Select the most recent dump
  Single number - Select one dump
"""
if __name__ == '__main__':
    # Parse command line arguments
    args = parse_args()

    # Determine which dumps to process
    if args.dumps:
        # User specified specific dumps
        dumps_to_process = args.dumps
        print(f"📋 Using specified dumps: {dumps_to_process}")
    elif args.year:
        # User specified a year - find available dumps for that year
        print(f"📅 Finding available Common Crawl dumps for year {args.year}...")
        available_dumps = get_available_dumps(args.year)

        if not available_dumps:
            print(f"❌ No dumps found for year {args.year}")
            exit(1)

        if args.non_interactive:
            # Non-interactive mode: use latest dump
            dumps_to_process = [available_dumps[0]]
            print(f"🤖 Non-interactive mode: Using latest dump {dumps_to_process[0]}")
        else:
            # Interactive mode: let user choose
            dumps_to_process = select_dumps_interactive(available_dumps)
            if not dumps_to_process:
                print("❌ No dumps selected")
                exit(1)
    else:
        # No year or dumps specified - show recent dumps and let user choose
        print("📊 Finding recent Common Crawl dumps...")
        available_dumps = get_available_dumps()

        if args.non_interactive:
            dumps_to_process = [available_dumps[0]]
            print(f"🤖 Non-interactive mode: Using latest dump {dumps_to_process[0]}")
        else:
            dumps_to_process = select_dumps_interactive(available_dumps)
            if not dumps_to_process:
                print("❌ No dumps selected")
                exit(1)

    print(f"🚀 Processing {len(dumps_to_process)} Common Crawl dumps: {dumps_to_process}")

    # Process dumps sequentially (can be parallelized later)
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
        try:
            main_processing_executor.run()
            print(f"✅ Successfully processed dump: {dump_id}")
        except Exception as e:
            print(f"❌ Failed to process dump {dump_id}: {e}")
            if len(dumps_to_process) == 1:
                exit(1)  # Exit if only one dump and it fails
            else:
                print("Continuing with remaining dumps...")

    # Only run deduplication in slurm mode (production)
    if args.mode == 'slurm' and not args.skip_dedup:
        print("\n🔄 Starting deduplication pipeline...")

        # For deduplication, we need to process all dumps together
        # This would require modifying the deduplication logic to handle multiple inputs
        print("⚠️  Multi-dump deduplication not yet implemented. Processing individual dumps.")

        print("✅ Production processing completed!")
    else:
        if args.skip_dedup:
            print("⏭️  Skipping deduplication as requested")
        print("✅ Local processing completed. Use --mode slurm for full production processing.")

