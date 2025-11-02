"""
FineWeb-Data: Universal domain-specific dataset processing pipeline based on FineWeb methodology

This pipeline can generate datasets for any domain/topic by using LLM-powered ontology-based
keyword generation and content filtering. Supports domains like education, environment,
quantum computing, finance, etc.
"""

import os
import re
import argparse
from dotenv import load_dotenv
import requests
from typing import List, Optional, Dict, Any
import json
import time
from dataclasses import dataclass

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

# Try to import InferenceRunner for LLM integration
try:
    from datatrove.pipeline.inference import InferenceRunner
    INFERENCE_RUNNER_AVAILABLE = True
except ImportError:
    INFERENCE_RUNNER_AVAILABLE = False
    print("⚠️  InferenceRunner not available - LLM scoring disabled")
    print("   Consider upgrading datatrove for LLM integration")

# Try to import OpenAI for ontology generation
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI not available - ontology generation will use fallback methods")


@dataclass
class DomainOntology:
    """Represents an ontology for a specific domain"""
    domain: str
    core_concepts: List[str]
    subdomains: List[str]
    keywords: List[str]
    technical_terms: List[str]
    context_indicators: List[str]
    quality_patterns: List[str]


DUMP_TO_PROCESS = "CC-MAIN-2023-50"  # example dump

MAIN_OUTPUT_PATH = "s3://fineweb-data"  # S3 bucket for production
FILTERING_OUTPUT_PATH = f"{MAIN_OUTPUT_PATH}/base_processing"

# Domain-specific ontologies will be generated dynamically
DOMAIN_ONTOLOGIES: Dict[str, DomainOntology] = {}


def generate_domain_ontology_llm(domain: str, llm_model: str = "gpt-4o-mini") -> DomainOntology:
    """
    Use LLM to generate a comprehensive ontology for a given domain.
    This creates a structured knowledge representation for content filtering.

    Args:
        domain (str): The domain/topic to analyze (e.g., "education", "quantum computing")
        llm_model (str): LLM model to use for ontology generation

    Returns:
        DomainOntology: Structured ontology containing keywords, concepts, and patterns
    """
    if not OPENAI_AVAILABLE:
        print("⚠️  OpenAI not available, using fallback ontology generation")
        return generate_fallback_ontology(domain)

    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        prompt = f"""
        Analyze the domain "{domain}" and create a comprehensive ontology for content filtering and dataset creation.

        Provide a detailed JSON structure containing:

        1. core_concepts: 5-10 fundamental concepts central to this domain
        2. subdomains: 5-8 specific sub-areas within this domain
        3. keywords: 50-100 specific keywords and phrases commonly used in this domain
        4. technical_terms: 20-40 specialized technical terms, jargon, and acronyms
        5. context_indicators: 10-15 phrases that indicate the content is discussing this domain seriously
        6. quality_patterns: 8-12 regex patterns that identify high-quality, domain-specific content

        Consider the domain from multiple perspectives:
        - Academic/research aspects
        - Professional/practical applications
        - Industry/business contexts
        - Educational/training contexts
        - Technical/engineering aspects (if applicable)

        Ensure the keywords cover both general and specialized terminology.

        Respond ONLY with valid JSON in this format:
        {{
            "core_concepts": ["concept1", "concept2", ...],
            "subdomains": ["subdomain1", "subdomain2", ...],
            "keywords": ["keyword1", "keyword2", ...],
            "technical_terms": ["term1", "term2", ...],
            "context_indicators": ["indicator1", "indicator2", ...],
            "quality_patterns": ["pattern1", "pattern2", ...]
        }}
        """

        response = client.chat.completions.create(
            model=llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )

        result = json.loads(response.choices[0].message.content.strip())

        return DomainOntology(
            domain=domain,
            core_concepts=result.get("core_concepts", []),
            subdomains=result.get("subdomains", []),
            keywords=result.get("keywords", []),
            technical_terms=result.get("technical_terms", []),
            context_indicators=result.get("context_indicators", []),
            quality_patterns=result.get("quality_patterns", [])
        )

    except Exception as e:
        print(f"❌ LLM ontology generation failed: {e}")
        print("Falling back to rule-based ontology generation")
        return generate_fallback_ontology(domain)


def generate_fallback_ontology(domain: str) -> DomainOntology:
    """
    Generate a basic ontology using rule-based methods when LLM is not available.
    """
    # Basic domain mappings for common topics
    domain_mappings = {
        "education": {
            "core_concepts": ["learning", "teaching", "curriculum", "assessment", "pedagogy"],
            "subdomains": ["k-12 education", "higher education", "special education", "online learning", "educational technology"],
            "keywords": ["student", "teacher", "classroom", "lesson", "curriculum", "assessment", "pedagogy", "learning objectives"],
            "technical_terms": ["bloom's taxonomy", "differentiated instruction", "scaffolding", "constructivism", "andragogy"],
            "context_indicators": ["educational research", "teaching methods", "learning outcomes", "academic achievement"],
            "quality_patterns": [r'\b(phd|masters|bachelors|doctorate)\b', r'\b(curriculum|pedagogy|assessment)\b']
        },
        "environment": {
            "core_concepts": ["sustainability", "climate change", "biodiversity", "conservation", "pollution"],
            "subdomains": ["climate science", "conservation biology", "environmental policy", "sustainable development", "ecology"],
            "keywords": ["climate", "environment", "sustainable", "conservation", "biodiversity", "pollution", "ecosystem"],
            "technical_terms": ["anthropogenic", "carbon footprint", "biodiversity hotspot", "sustainable development goals"],
            "context_indicators": ["environmental impact", "climate policy", "conservation efforts", "sustainable practices"],
            "quality_patterns": [r'\b(climate change|global warming)\b', r'\b(sustainability|sustainable development)\b']
        },
        "quantum computing": {
            "core_concepts": ["quantum mechanics", "superposition", "entanglement", "qubits", "quantum algorithms"],
            "subdomains": ["quantum algorithms", "quantum hardware", "quantum cryptography", "quantum sensing", "quantum simulation"],
            "keywords": ["quantum", "qubit", "superposition", "entanglement", "quantum gate", "quantum circuit"],
            "technical_terms": ["hadamard gate", "cnot gate", "shor's algorithm", "grover's algorithm", "quantum supremacy"],
            "context_indicators": ["quantum advantage", "quantum speedup", "quantum error correction", "quantum volume"],
            "quality_patterns": [r'\b(quantum (computing|algorithm|circuit))\b', r'\b(qubit|superposition|entanglement)\b']
        }
    }

    if domain.lower() in domain_mappings:
        mapping = domain_mappings[domain.lower()]
        return DomainOntology(
            domain=domain,
            core_concepts=mapping["core_concepts"],
            subdomains=mapping["subdomains"],
            keywords=mapping["keywords"],
            technical_terms=mapping["technical_terms"],
            context_indicators=mapping["context_indicators"],
            quality_patterns=mapping["quality_patterns"]
        )
    else:
        # Generic fallback for unknown domains
        return DomainOntology(
            domain=domain,
            core_concepts=["research", "analysis", "methodology", "applications"],
            subdomains=["theory", "practice", "applications", "case studies"],
            keywords=[domain.lower(), f"{domain} research", f"{domain} analysis"],
            technical_terms=[],
            context_indicators=[f"{domain} related", f"professional {domain}"],
            quality_patterns=[r'\b(research|analysis|methodology)\b']
        )


def get_domain_keywords(domain: str) -> List[str]:
    """Get all keywords for a domain, combining different categories."""
    if domain not in DOMAIN_ONTOLOGIES:
        print(f"🔍 Generating ontology for domain: {domain}")
        ontology = generate_domain_ontology_llm(domain)
        DOMAIN_ONTOLOGIES[domain] = ontology

    ontology = DOMAIN_ONTOLOGIES[domain]
    return ontology.keywords + ontology.technical_terms + ontology.context_indicators


def domain_relevance_scorer(text: str, domain: str) -> float:
    """
    Score domain relevance using ontology-based keyword matching.

    This function calculates a relevance score from 0-5 based on:
    - Density of domain-specific keywords
    - Presence of core concepts and technical terms
    - Context indicators for domain relevance
    """
    if domain not in DOMAIN_ONTOLOGIES:
        ontology = generate_domain_ontology_llm(domain)
        DOMAIN_ONTOLOGIES[domain] = ontology
    else:
        ontology = DOMAIN_ONTOLOGIES[domain]

    text_lower = text.lower()

    # Count different types of keywords with different weights
    core_concept_count = sum(1 for concept in ontology.core_concepts if concept.lower() in text_lower)
    keyword_count = sum(1 for keyword in ontology.keywords if keyword.lower() in text_lower)
    technical_count = sum(1 for term in ontology.technical_terms if term.lower() in text_lower)
    context_count = sum(1 for indicator in ontology.context_indicators if indicator in text_lower)

    # Calculate density score with weighted components
    word_count = len(text.split())
    if word_count == 0:
        return 0.0

    # Weighted scoring: technical terms and core concepts have higher weight
    weighted_score = (
        core_concept_count * 3 +      # Core concepts: highest weight
        technical_count * 2 +         # Technical terms: high weight
        keyword_count * 1.5 +         # Keywords: medium weight
        context_count * 1             # Context indicators: base weight
    )

    density_score = weighted_score / word_count * 100

    # Boost score for strong domain indicators
    boost_multiplier = 1.0
    if core_concept_count >= 1:
        boost_multiplier += 0.3
    if technical_count >= 1:
        boost_multiplier += 0.4
    if context_count >= 2:
        boost_multiplier += 0.3

    # Final score (0-5 scale) with boost
    score = min(5.0, density_score * boost_multiplier / 10)

    return score


def domain_quality_filter(text: str, domain: str, threshold: float = 2.0) -> bool:
    """
    Enhanced domain-specific quality filter using ontology-based heuristics.
    """
    text_lower = text.lower()

    if domain not in DOMAIN_ONTOLOGIES:
        ontology = generate_domain_ontology_llm(domain)
        DOMAIN_ONTOLOGIES[domain] = ontology
    else:
        ontology = DOMAIN_ONTOLOGIES[domain]

    # Must have minimum domain relevance score
    score = domain_relevance_scorer(text, domain)
    if score < threshold:
        return False

    # Check for quality patterns specific to the domain
    pattern_matches = sum(1 for pattern in ontology.quality_patterns
                         if re.search(pattern, text_lower, re.IGNORECASE))

    # Additional quality checks
    has_core_concept = any(concept.lower() in text_lower for concept in ontology.core_concepts)
    has_technical_term = any(term.lower() in text_lower for term in ontology.technical_terms)

    # Pass if it has good score OR quality patterns OR both core concepts and technical terms
    return score >= 3.0 or pattern_matches >= 1 or (has_core_concept and has_technical_term)


def is_domain_content(text: str, domain: str, threshold: int = 2) -> bool:
    """
    Enhanced domain content detection with multiple criteria:
    1. Contains multiple domain-specific keywords
    2. Has domain context (not just casual mentions)
    3. Uses ontology-based quality heuristics
    """
    text_lower = text.lower()

    if domain not in DOMAIN_ONTOLOGIES:
        ontology = generate_domain_ontology_llm(domain)
        DOMAIN_ONTOLOGIES[domain] = ontology
    else:
        ontology = DOMAIN_ONTOLOGIES[domain]

    # Count domain-specific keywords
    keyword_count = sum(1 for keyword in ontology.keywords if keyword.lower() in text_lower)
    technical_count = sum(1 for term in ontology.technical_terms if term.lower() in text_lower)

    # Basic threshold: at least threshold domain keywords OR technical terms
    if keyword_count + technical_count < threshold:
        return False

    # Additional context validation
    context_count = sum(1 for indicator in ontology.context_indicators if indicator in text_lower)
    core_concept_count = sum(1 for concept in ontology.core_concepts if concept.lower() in text_lower)

    # Use the enhanced domain quality filter
    quality_pass = domain_quality_filter(text, domain, threshold=1.5)

    # Require strong domain indicators OR quality filter pass
    return (context_count >= 1 or core_concept_count >= 1 or keyword_count >= 3) and quality_pass


def parse_llm_score(llm_output: str) -> float:
    """
    Robustly parse LLM score from output string.
    Handles various formats and edge cases.
    """
    if not llm_output:
        return 0.0

    cleaned = llm_output.strip()

    # Try to extract numeric score using regex
    score_patterns = [
        r'(?:score[:\s]*|rating[:\s]*|)(\d+(?:\.\d+)?)',  # "score: 3.5" or just "3.5"
        r'^(\d+(?:\.\d+)?)$',  # Just the number
        r'(\d+(?:\.\d+)?).*?(?:/|out of).*?5',  # "3/5" format
    ]

    for pattern in score_patterns:
        match = re.search(pattern, cleaned, re.IGNORECASE)
        if match:
            try:
                score = float(match.group(1))
                return max(0.0, min(5.0, score))
            except ValueError:
                continue

    # Default to 0 if parsing completely fails
    print(f"⚠️  Could not parse LLM score from output: '{cleaned}'")
    return 0.0


def run_domain_benchmarks(args):
    """
    Run benchmark tests on domain-specific LLM performance using diverse samples.
    """
    print(f"🏆 FineWeb-Data Benchmark Suite for Domain: {args.domain}")
    print("=" * 60)

    # Generate domain ontology
    if args.domain not in DOMAIN_ONTOLOGIES:
        ontology = generate_domain_ontology_llm(args.domain)
        DOMAIN_ONTOLOGIES[args.domain] = ontology

    ontology = DOMAIN_ONTOLOGIES[args.domain]

    print(f"📚 Domain Ontology Generated:")
    print(f"  Core Concepts: {len(ontology.core_concepts)}")
    print(f"  Keywords: {len(ontology.keywords)}")
    print(f"  Technical Terms: {len(ontology.technical_terms)}")
    print(f"  Context Indicators: {len(ontology.context_indicators)}")

    # Create test samples (in a real implementation, you'd load from domain-specific datasets)
    test_texts = [
        f"This is a comprehensive guide to {args.domain} principles and applications.",
        f"Recent research in {args.domain} has shown significant advancements.",
        f"The fundamentals of {args.domain} include {', '.join(ontology.core_concepts[:3])}.",
        f"Professional {args.domain} practitioners use specialized tools and methodologies.",
        f"Academic study of {args.domain} requires understanding complex theoretical frameworks.",
        "The weather today is sunny and warm, perfect for outdoor activities.",
        "Stock market analysis shows bullish trends in technology sector investments.",
        "Cooking recipes for chocolate chip cookies require flour, sugar, and butter."
    ]

    print(f"\n📋 Testing {len(test_texts)} text samples...")

    results = []
    for i, text in enumerate(test_texts, 1):
        print(f"\n🔬 Test {i}: {text[:60]}{'...' if len(text) > 60 else ''}")

        # Test keyword-based scoring
        keyword_score = domain_relevance_scorer(text, args.domain)
        print(f"  Domain Score: {keyword_score:.2f}")

        # Test quality filter
        quality_pass = domain_quality_filter(text, args.domain)
        print(f"  Quality Filter: {'✅ PASS' if quality_pass else '❌ FAIL'}")

        # Test enhanced domain content detection
        content_pass = is_domain_content(text, args.domain, args.domain_threshold)
        print(f"  Content Filter: {'✅ PASS' if content_pass else '❌ FAIL'}")

        results.append({
            'text_id': i,
            'text': text,
            'keyword_score': keyword_score,
            'quality_pass': quality_pass,
            'content_pass': content_pass,
            'is_domain': i <= 5  # First 5 are domain-related, rest are not
        })

    # Summary statistics
    domain_results = [r for r in results if r['is_domain']]
    non_domain_results = [r for r in results if not r['is_domain']]

    print("\n📊 Benchmark Results Summary:")
    print(f"  Total samples: {len(results)} ({len(domain_results)} domain + {len(non_domain_results)} non-domain)")

    # Domain content performance
    domain_quality_pass = sum(1 for r in domain_results if r['quality_pass'])
    domain_content_pass = sum(1 for r in domain_results if r['content_pass'])
    print("\n🎯 Domain Content Detection:")
    print(f"  Quality filter: {domain_quality_pass}/{len(domain_results)} ({domain_quality_pass/len(domain_results)*100:.1f}%) true positive rate")
    print(f"  Content filter: {domain_content_pass}/{len(domain_results)} ({domain_content_pass/len(domain_results)*100:.1f}%) true positive rate")

    # False positive check
    non_domain_quality_pass = sum(1 for r in non_domain_results if r['quality_pass'])
    non_domain_content_pass = sum(1 for r in non_domain_results if r['content_pass'])
    print("\n🚫 False Positive Detection:")
    print(f"  Quality filter: {non_domain_quality_pass}/{len(non_domain_results)} ({non_domain_quality_pass/len(non_domain_results)*100:.1f}%) false positive rate")
    print(f"  Content filter: {non_domain_content_pass}/{len(non_domain_results)} ({non_domain_content_pass/len(non_domain_results)*100:.1f}%) false positive rate")

    print(f"  Average domain keyword score: {sum(r['keyword_score'] for r in domain_results)/len(domain_results):.2f}")
    print(f"  Average non-domain keyword score: {sum(r['keyword_score'] for r in non_domain_results)/len(non_domain_results):.2f}")

    print("\n🎯 Domain Filtering Effectiveness:")
    print("  ✅ Ontology-based filtering: Uses domain-specific knowledge structures")
    print("  ✅ Multi-layer validation: Combines keyword, concept, and quality checks")
    print("  ✅ Context awareness: Considers domain-specific patterns and terminology")
    print("  ✅ Adaptive scoring: Weights different types of domain indicators")

    if args.use_llm_scoring:
        print("  ✅ LLM enhancement: Advanced semantic understanding available")
    else:
        print("  💡 Tip: Enable --use-llm-scoring for enhanced domain relevance detection")

    print("\n✅ Benchmark completed successfully!")


def get_available_dumps(year: Optional[int] = None) -> List[str]:
    """
    Get available Common Crawl dumps for a specific year or all recent dumps.
    Uses Common Crawl's index API for accurate and up-to-date information.
    """
    dumps = []

    # Try to fetch from Common Crawl index API (more reliable)
    try:
        response = requests.get('https://index.commoncrawl.org/collinfo.json', timeout=15)
        if response.status_code == 200:
            index_data = response.json()
            # Extract CC-MAIN dumps
            dumps = [item['id'] for item in index_data if item['id'].startswith('CC-MAIN-')]
            dumps.sort(reverse=True)  # Most recent first
    except Exception as e:
        print(f"⚠️  Failed to fetch from Common Crawl index API: {e}")

    # Fallback: comprehensive list including latest 2025 dumps (updated as of November 2025)
    if not dumps:
        fallback_dumps = [
            # 2025 dumps (latest available as of November 2025)
            'CC-MAIN-2025-43', 'CC-MAIN-2025-42', 'CC-MAIN-2025-40', 'CC-MAIN-2025-38',
            'CC-MAIN-2025-36', 'CC-MAIN-2025-33', 'CC-MAIN-2025-30', 'CC-MAIN-2025-26',
            'CC-MAIN-2025-22', 'CC-MAIN-2025-18', 'CC-MAIN-2025-15', 'CC-MAIN-2025-11',
            'CC-MAIN-2025-08', 'CC-MAIN-2025-05', 'CC-MAIN-2025-01',
            # 2024 dumps (complete)
            'CC-MAIN-2024-51', 'CC-MAIN-2024-50', 'CC-MAIN-2024-49', 'CC-MAIN-2024-46',
            'CC-MAIN-2024-42', 'CC-MAIN-2024-38', 'CC-MAIN-2024-33', 'CC-MAIN-2024-30',
            'CC-MAIN-2024-26', 'CC-MAIN-2024-22', 'CC-MAIN-2024-18', 'CC-MAIN-2024-15',
            'CC-MAIN-2024-10', 'CC-MAIN-2024-05',
            # 2023 dumps
            'CC-MAIN-2023-50', 'CC-MAIN-2023-40', 'CC-MAIN-2023-23', 'CC-MAIN-2023-06',
            # 2022 dumps (for completeness)
            'CC-MAIN-2022-49', 'CC-MAIN-2022-40', 'CC-MAIN-2022-33', 'CC-MAIN-2022-27'
        ]
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


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='FineWeb-Data: Universal domain-specific dataset processing pipeline')

    parser.add_argument('--domain', required=True,
                       help='Target domain for dataset creation (e.g., education, environment, quantum-computing)')

    parser.add_argument('--mode', choices=['local', 'slurm'],
                       default='local',
                       help='Execution mode: local or slurm cluster (default: local)')

    parser.add_argument('--cluster-name',
                       default='fineweb-data-slurm-cluster',
                       help='Slurm cluster name (only used in slurm mode)')

    parser.add_argument('--year', type=int,
                       help='Year to process (will show available dumps for that year)')

    parser.add_argument('--dumps', nargs='+',
                       help='Specific Common Crawl dumps to process (alternative to --year)')

    parser.add_argument('--output-bucket', default='fineweb-data',
                       help='S3 bucket name for output (default: fineweb-data)')

    parser.add_argument('--min-words', type=int, default=200,
                       help='Minimum word count for documents (default: 200)')

    parser.add_argument('--domain-threshold', type=int, default=2,
                       help='Minimum number of domain keywords required (default: 2)')

    parser.add_argument('--compression', choices=['gzip', 'none'], default='gzip',
                       help='Output compression format (default: gzip)')

    parser.add_argument('--skip-dedup', action='store_true',
                       help='Skip deduplication step (useful for testing)')

    parser.add_argument('--non-interactive', action='store_true',
                       help='Skip interactive dump selection (use latest dump)')

    if INFERENCE_RUNNER_AVAILABLE:
        parser.add_argument('--use-llm-scoring', action='store_true',
                           help='Use LLM-based domain relevance scoring (requires GPU/cluster)')

        parser.add_argument('--llm-model', default='meta-llama/Llama-3-8B-Instruct',
                           help='LLM model for domain relevance scoring (from HF)')

        parser.add_argument('--domain-threshold-llm', type=float, default=3.0,
                           help='Minimum LLM domain relevance score (0-5)')

        parser.add_argument('--gpu', action='store_true',
                           help='Use GPU partition for LLM inference in Slurm')
    else:
        # Add dummy arguments that show warnings when used
        parser.add_argument('--use-llm-scoring', action='store_true',
                           help='LLM scoring not available in current datatrove version')

        parser.add_argument('--llm-model', default='meta-llama/Llama-3-8B-Instruct',
                           help='LLM model (not available)')

        parser.add_argument('--domain-threshold-llm', type=float, default=3.0,
                           help='LLM threshold (not available)')

        parser.add_argument('--gpu', action='store_true',
                           help='GPU mode (LLM not available)')

    parser.add_argument('--benchmark', action='store_true',
                       help='Run benchmark tests on domain-specific LLM performance')

    return parser.parse_args()


def create_executor(mode, cluster_name, dumps, output_bucket, domain, min_words=200,
                   domain_threshold=2, compression='gzip', skip_dedup=False,
                   use_llm_scoring=False, llm_model='meta-llama/Llama-3-8B-Instruct',
                   domain_threshold_llm=3.0, gpu=False):
    """Create the appropriate executor based on mode."""

    # Update global variables based on arguments
    global DUMP_TO_PROCESS, MAIN_OUTPUT_PATH, FILTERING_OUTPUT_PATH
    # Use the first dump as primary for backward compatibility, but support multiple
    DUMP_TO_PROCESS = dumps[0] if isinstance(dumps, list) else dumps
    MAIN_OUTPUT_PATH = f"s3://{output_bucket}"
    FILTERING_OUTPUT_PATH = f"{MAIN_OUTPUT_PATH}/base_processing"

    # Generate domain ontology if not already cached
    if domain not in DOMAIN_ONTOLOGIES:
        print(f"🔍 Generating ontology for domain: {domain}")
        ontology = generate_domain_ontology_llm(domain)
        DOMAIN_ONTOLOGIES[domain] = ontology

    ontology = DOMAIN_ONTOLOGIES[domain]
    print(f"📚 Using domain ontology with {len(ontology.keywords)} keywords, {len(ontology.technical_terms)} technical terms")

    pipeline = [
        WarcReader(
            data_folder=f"s3://commoncrawl/crawl-data/{DUMP_TO_PROCESS}/segments/",
            glob_pattern="*/warc/*",  # we want the warc files
            default_metadata={"dump": DUMP_TO_PROCESS, "dataset": f"fineweb-{domain.replace(' ', '-')}"},
        ),
        URLFilter(exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/1_url/{DUMP_TO_PROCESS}")),
        Trafilatura(favour_precision=True, timeout=2),  # Slightly longer timeout for domain content
        LanguageFilter(
            exclusion_writer=JsonlWriter(
                f"{FILTERING_OUTPUT_PATH}/2_non_english/",
                output_filename="${language}/" + DUMP_TO_PROCESS + "/${rank}.jsonl.gz",
            )
        ),
        # Enhanced domain content filter - more sophisticated filtering
        LambdaFilter(
            lambda doc: is_domain_content(doc.text, domain, domain_threshold),
            exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/3_non_domain/{DUMP_TO_PROCESS}")
        ),
        # Minimum length filter - domain documents should be substantial
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
        )
    ]

    # Add PerplexityFilter if available (outside pipeline list)
    try:
        from datatrove.pipeline.filters import PerplexityFilter
        pipeline.append(
            PerplexityFilter(
                exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/9_perplexity/{DUMP_TO_PROCESS}")
            )
        )
    except ImportError:
        # PerplexityFilter not available, skip this step
        pass

    # LLM-based domain relevance scoring (if enabled and available)
    if use_llm_scoring and INFERENCE_RUNNER_AVAILABLE:
        domain_prompt = (
            f"Score this text's relevance to the domain '{domain}' for LLM training on a scale of 0-5, "
            f"where 5 means highly educational/professional content suitable for {domain} AI training, "
            f"and 0 means not relevant at all. Consider {domain} terminology, domain context, "
            f"research quality, and educational value. Consider these key aspects: "
            f"{', '.join(ontology.core_concepts[:5])}. Provide only the numeric score.\n\n"
            f"Text: {{text}}\n\nScore:"
        )
        pipeline.append(
            InferenceRunner(
                inference_engine="vllm",
                model_path=llm_model,
                prompt_template=domain_prompt,
                generation_config={"max_tokens": 10, "temperature": 0.1},
                output_key="llm_domain_score",
                batch_size=8 if gpu else 1,  # Smaller batch for CPU, larger for GPU
            )
        )
        # Filter based on LLM score
        pipeline.append(
            LambdaFilter(
                lambda doc: parse_llm_score(doc.metadata.get("llm_domain_score", "")) >= domain_threshold_llm,
                exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/10_llm_low_score/{DUMP_TO_PROCESS}")
            )
        )
    elif use_llm_scoring and not INFERENCE_RUNNER_AVAILABLE:
        print("⚠️  LLM scoring requested but InferenceRunner not available - skipping LLM step")
        print("   Continuing with ontology-based filtering only")

    # Enhanced PII removal - general purpose (not domain-specific like medical)
    pipeline.extend([
        PIIFormatter(
            remove_emails=True,
            remove_ips=True,
            only_remove_public_ips=True,  # Only remove public IPs, keep private ones
            email_replacement=('email@example.com', 'firstname.lastname@example.org'),
            ip_replacement=('22.214.171.124', '126.96.36.199', '188.8.131.52', '184.108.40.206', '220.127.116.11', '18.104.22.168')
        ),
        TokensCounter(),
        JsonlWriter(f"{FILTERING_OUTPUT_PATH}/output/{DUMP_TO_PROCESS}", compression=compression if compression != 'none' else None),
    ])

    if mode == 'local':
        # Local mode for testing and development
        print("🔧 Running in LOCAL mode")
        print(f"📁 Processing dump: {DUMP_TO_PROCESS}")
        print(f"🎯 Target domain: {domain}")
        if not (use_llm_scoring and INFERENCE_RUNNER_AVAILABLE):
            print("⚠️  Limited to 100 documents per task for testing (remove limit with --use-llm-scoring for full processing)")
            pipeline[0] = WarcReader(
                data_folder=f"s3://commoncrawl/crawl-data/{DUMP_TO_PROCESS}/segments/",
                glob_pattern="*/warc/*",
                default_metadata={"dump": DUMP_TO_PROCESS, "dataset": f"fineweb-{domain.replace(' ', '-')}"},
                limit=100,  # Limit for local testing
            )
        else:
            print("⚠️  LLM scoring enabled - processing full dump (may be slow on local machine)")
            # Keep original pipeline for full processing when LLM is enabled

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
        print(f"🎯 Target domain: {domain}")
        if use_llm_scoring:
            print("🤖 LLM scoring enabled - using GPU resources")
        if gpu:
            print("🖥️  GPU mode enabled")

        # Adjust resources based on LLM usage
        if (use_llm_scoring and INFERENCE_RUNNER_AVAILABLE) or gpu:
            partition = "hopper-gpu" if gpu else "hopper-cpu"
            cpus_per_task = 4
            mem_per_cpu_gb = 8  # More memory for GPU tasks
            time_limit = "48:00:00"  # Longer time for LLM processing
        else:
            partition = "hopper-cpu"
            cpus_per_task = 2
            mem_per_cpu_gb = 4
            time_limit = "24:00:00"

        executor = SlurmPipelineExecutor(
            job_name=f"fineweb_{domain.replace(' ', '_')}_{DUMP_TO_PROCESS}",
            pipeline=pipeline,
            tasks=8000 if (use_llm_scoring and INFERENCE_RUNNER_AVAILABLE) else 6000,  # More tasks for production
            time=time_limit,
            logging_dir=f"{MAIN_OUTPUT_PATH}/logs/base_processing/{DUMP_TO_PROCESS}",
            slurm_logs_folder=f"logs/base_processing/{DUMP_TO_PROCESS}/slurm_logs",
            randomize_start_duration=300,  # More randomization
            mem_per_cpu_gb=mem_per_cpu_gb,
            cpus_per_task=cpus_per_task,
            partition=partition,
        )

    return executor


"""
Command Line Usage Examples:

# Basic usage - create education dataset
python finewebdata.py --domain education --mode local

# Create environment dataset with LLM enhancement
python finewebdata.py --domain environment --mode slurm --use-llm-scoring --gpu

# Create quantum computing dataset from specific year
python finewebdata.py --domain "quantum computing" --year 2024

# Benchmark domain detection performance
python finewebdata.py --domain education --benchmark

# Production run with custom settings
python finewebdata.py --domain "artificial intelligence" --mode slurm --year 2025 --output-bucket fineweb-ai --min-words 250 --domain-threshold 3 --compression gzip --non-interactive

Domain Examples:
- education (pedagogy, curriculum, learning)
- environment (sustainability, climate, conservation)
- "quantum computing" (qubits, superposition, entanglement)
- finance (investment, markets, risk management)
- healthcare (medical, clinical, patient care)
- "machine learning" (algorithms, training, neural networks)

Selection Options (when interactive):
  'all' - Select all available dumps
  '1,3,5' - Select specific dumps by number
  '1-5' - Select range of dumps
  'latest' - Select the most recent dump
  Single number - Select one dump
"""
if __name__ == '__main__':
    # Parse command line arguments
    args = parse_args()

    # Run benchmark if requested
    if args.benchmark:
        print("🏆 Running domain benchmark tests...")
        run_domain_benchmarks(args)
        exit(0)

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
    print(f"🎯 Target domain: {args.domain}")

    # Process dumps with retry logic and parallelization support
    import time
    failed_dumps = []

    for dump_id in dumps_to_process:
        print(f"\n🔄 Processing dump: {dump_id}")

        max_retries = 3
        retry_delay = 60  # seconds

        for attempt in range(max_retries):
            try:
                # Create executor based on mode
                main_processing_executor = create_executor(
                    mode=args.mode,
                    cluster_name=args.cluster_name,
                    dumps=[dump_id],  # Pass as list for consistency
                    output_bucket=args.output_bucket,
                    domain=args.domain,
                    min_words=args.min_words,
                    domain_threshold=args.domain_threshold,
                    compression=args.compression,
                    skip_dedup=args.skip_dedup,
                    use_llm_scoring=args.use_llm_scoring,
                    llm_model=args.llm_model,
                    domain_threshold_llm=args.domain_threshold_llm,
                    gpu=args.gpu
                )

                # Launch the base processing pipeline for this dump
                main_processing_executor.run()
                print(f"✅ Successfully processed dump: {dump_id}")
                break  # Success, exit retry loop

            except Exception as e:
                print(f"❌ Attempt {attempt + 1}/{max_retries} failed for dump {dump_id}: {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print(f"💥 All retry attempts failed for dump {dump_id}")
                    failed_dumps.append(dump_id)
                    if len(dumps_to_process) == 1:
                        print("❌ Only dump failed, exiting...")
                        exit(1)
                    else:
                        print("Continuing with remaining dumps...")

    if failed_dumps:
        print(f"\n⚠️  Warning: {len(failed_dumps)} dumps failed: {failed_dumps}")
        print("Check logs for details. You may need to re-run these dumps manually.")

    # Only run deduplication in slurm mode (production)
    if args.mode == 'slurm' and not args.skip_dedup:
        print("\n🔄 Starting deduplication pipeline...")

        # Collect all processed dump outputs for deduplication
        input_paths = []
        for dump_id in dumps_to_process:
            output_path = f"{FILTERING_OUTPUT_PATH}/output/{dump_id}"
            input_paths.append(f"{output_path}/*.jsonl.gz")

        if not input_paths:
            print("⚠️  No processed dumps found for deduplication - skipping")
        elif input_paths:
            # Create deduplication pipeline
            dedup_config = MinhashConfig(
                hash_config=HashConfig(
                    hash_length=64,
                    num_hashes=8,
                    num_buckets=14,
                    seed=42
                ),
                num_bands=10,
                num_minhashes_per_band=5
            )

            dedup_pipeline = [
                JsonlReader(
                    data_folder=input_paths,
                    default_metadata={"dataset": f"fineweb-{args.domain.replace(' ', '-')}-deduplicated"}
                ),
                MinhashDedupSignature(
                    config=dedup_config,
                    input_key="text"
                ),
                MinhashDedupBuckets(
                    config=dedup_config
                ),
                MinhashDedupFilter(
                    config=dedup_config,
                    exclusion_writer=JsonlWriter(f"{FILTERING_OUTPUT_PATH}/removed/dedup/")
                ),
                TokensCounter(),
                JsonlWriter(
                    f"{FILTERING_OUTPUT_PATH}/deduplicated/",
                    compression=args.compression if args.compression != 'none' else None
                )
            ]

            # Create deduplication executor
            dedup_executor = SlurmPipelineExecutor(
                job_name=f"fineweb_{args.domain.replace(' ', '_')}_dedup",
                pipeline=dedup_pipeline,
                tasks=2000,  # Fewer tasks for deduplication
                time="12:00:00",
                logging_dir=f"{MAIN_OUTPUT_PATH}/logs/dedup/",
                slurm_logs_folder="logs/dedup/slurm_logs",
                randomize_start_duration=180,
                mem_per_cpu_gb=4,
                cpus_per_task=2,
                partition="hopper-cpu",
            )

            try:
                dedup_executor.run()
                print("✅ Deduplication completed successfully!")
            except Exception as e:
                print(f"❌ Deduplication failed: {e}")
        else:
            print("⚠️  No processed dumps found for deduplication")

        print("✅ Production processing completed!")
    else:
        if args.skip_dedup:
            print("⏭️  Skipping deduplication as requested")
        print("✅ Local processing completed. Use --mode slurm for full production processing.")
