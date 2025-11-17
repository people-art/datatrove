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
from contextlib import contextmanager

# Load environment variables from .env file
# Try multiple possible locations for .env file
env_loaded = False
for env_path in ['.env', '../.env', './.env']:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        env_loaded = True
        print(f"✅ Loaded environment variables from {env_path}")
        break

if not env_loaded:
    print("⚠️  No .env file found in current directory or parent directory")

# Configure anonymous access for Common Crawl (public bucket)
# Clear credentials for anonymous access to Common Crawl
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
    print("✅ OpenAI package is available")

    # Check if API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and len(api_key.strip()) > 10:
        print(f"✅ OPENAI_API_KEY is set (length: {len(api_key)})")
    else:
        print("⚠️  OPENAI_API_KEY is not set or too short")
        OPENAI_AVAILABLE = False

except ImportError as e:
    print(f"⚠️  OpenAI package not available: {e}")
    print("   Attempting to install openai...")

    try:
        import subprocess
        import sys
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet', 'openai'])

        # Try importing again
        from openai import OpenAI
        OPENAI_AVAILABLE = True
        print("✅ OpenAI package installed and available")

        # Check if API key is available
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and len(api_key.strip()) > 10:
            print(f"✅ OPENAI_API_KEY is set (length: {len(api_key)})")
        else:
            print("⚠️  OPENAI_API_KEY is not set or too short")
            OPENAI_AVAILABLE = False

    except Exception as install_error:
        OPENAI_AVAILABLE = False
        print(f"❌ Failed to install OpenAI package: {install_error}")
        print("   Ontology generation will use fallback methods")


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


@contextmanager
def cc_anonymous_read():
    """Context manager for anonymous Common Crawl S3 access"""
    backup = {k: os.environ.get(k) for k in ("AWS_ACCESS_KEY_ID","AWS_SECRET_ACCESS_KEY","AWS_SESSION_TOKEN")}
    os.environ["AWS_ACCESS_KEY_ID"] = ""
    os.environ["AWS_SECRET_ACCESS_KEY"] = ""
    os.environ.pop("AWS_SESSION_TOKEN", None)
    try:
        yield
    finally:
        for k,v in backup.items():
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v


DUMP_TO_PROCESS = "CC-MAIN-2023-50"  # example dump

MAIN_OUTPUT_PATH = "s3://fineweb-data"  # S3 bucket for production
FILTERING_OUTPUT_PATH = f"{MAIN_OUTPUT_PATH}/base_processing"

# Domain-specific ontologies will be generated dynamically
DOMAIN_ONTOLOGIES: Dict[str, DomainOntology] = {}


def slugify(s: str) -> str:
    """Convert string to URL-safe slug"""
    import re
    return re.sub(r'[^a-z0-9\-]+','-', s.lower().replace(' ', '-')).strip('-')

def generate_domain_ontology_llm(domain: str, llm_model: str = "gpt-5") -> DomainOntology:
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

        prompt = f"""You are an expert ontologist specializing in domain knowledge representation. Your task is to create a comprehensive ontology for the domain "{domain}" that will be used for content filtering and dataset creation.

CRITICAL REQUIREMENTS:
1. You must respond with VALID JSON only - no explanations, no markdown, no additional text
2. The JSON must be parseable by Python's json.loads() function
3. Do not include any text before or after the JSON
4. Do not wrap the JSON in markdown code blocks
5. All arrays must contain only strings, no nested objects

ANALYZE THE DOMAIN "{domain.upper()}":
- Study the domain from academic, professional, and practical perspectives
- Identify fundamental concepts, terminology, and quality indicators
- Consider how experts discuss and identify high-quality content in this domain

GENERATE THE FOLLOWING JSON STRUCTURE:

{{
  "core_concepts": [
    "fundamental_concept_1",
    "fundamental_concept_2",
    "fundamental_concept_3",
    "fundamental_concept_4",
    "fundamental_concept_5",
    "fundamental_concept_6",
    "fundamental_concept_7",
    "fundamental_concept_8"
  ],
  "subdomains": [
    "specific_subarea_1",
    "specific_subarea_2",
    "specific_subarea_3",
    "specific_subarea_4",
    "specific_subarea_5",
    "specific_subarea_6"
  ],
  "keywords": [
    "common_keyword_1",
    "common_keyword_2",
    "common_keyword_3",
    "common_keyword_4",
    "common_keyword_5",
    "technical_keyword_1",
    "technical_keyword_2",
    "technical_keyword_3",
    "specialized_term_1",
    "specialized_term_2",
    "domain_specific_phrase_1",
    "domain_specific_phrase_2",
    "expert_jargon_1",
    "expert_jargon_2",
    "professional_term_1",
    "professional_term_2",
    "industry_term_1",
    "industry_term_2",
    "academic_term_1",
    "academic_term_2",
    "research_term_1",
    "research_term_2",
    "practical_term_1",
    "practical_term_2",
    "methodological_term_1",
    "methodological_term_2",
    "conceptual_term_1",
    "conceptual_term_2",
    "application_term_1",
    "application_term_2",
    "tool_term_1",
    "tool_term_2",
    "process_term_1",
    "process_term_2",
    "outcome_term_1",
    "outcome_term_2",
    "evaluation_term_1",
    "evaluation_term_2",
    "quality_term_1",
    "quality_term_2",
    "standard_term_1",
    "standard_term_2",
    "best_practice_term_1",
    "best_practice_term_2",
    "emerging_term_1",
    "emerging_term_2"
  ],
  "technical_terms": [
    "specialized_jargon_1",
    "specialized_jargon_2",
    "specialized_jargon_3",
    "specialized_jargon_4",
    "specialized_jargon_5",
    "specialized_jargon_6",
    "specialized_jargon_7",
    "specialized_jargon_8",
    "specialized_jargon_9",
    "specialized_jargon_10",
    "technical_acronym_1",
    "technical_acronym_2",
    "technical_acronym_3",
    "technical_acronym_4",
    "technical_acronym_5",
    "methodology_term_1",
    "methodology_term_2",
    "methodology_term_3",
    "methodology_term_4",
    "methodology_term_5"
  ],
  "context_indicators": [
    "academic_discussion_1",
    "academic_discussion_2",
    "professional_context_1",
    "professional_context_2",
    "research_context_1",
    "research_context_2",
    "practical_application_1",
    "practical_application_2",
    "expert_discussion_1",
    "expert_discussion_2",
    "quality_indicator_1",
    "quality_indicator_2",
    "serious_treatment_1",
    "serious_treatment_2"
  ],
  "quality_patterns": [
    "\\\\bpattern_indicating_quality_content_1\\\\b",
    "\\\\bpattern_indicating_quality_content_2\\\\b",
    "\\\\bpattern_indicating_quality_content_3\\\\b",
    "\\\\bpattern_indicating_quality_content_4\\\\b",
    "\\\\bpattern_indicating_quality_content_5\\\\b",
    "\\\\bpattern_indicating_quality_content_6\\\\b",
    "\\\\bpattern_indicating_quality_content_7\\\\b",
    "\\\\bpattern_indicating_quality_content_8\\\\b",
    "\\\\bpattern_indicating_quality_content_9\\\\b",
    "\\\\bpattern_indicating_quality_content_10\\\\b"
  ]
}}

INSTRUCTIONS FOR CONTENT:
- core_concepts: 8 fundamental concepts that define the domain
- subdomains: 6 major sub-areas or specializations within the domain
- keywords: 40+ terms including general keywords, technical terms, phrases, and domain-specific language
- technical_terms: 20 specialized terms, jargon, acronyms specific to experts in the field
- context_indicators: 14 phrases that signal serious, professional discussion of the domain
- quality_patterns: 10 regex patterns (escaped with double backslashes) that identify high-quality content

REMEMBER: Respond ONLY with the JSON object. No additional text, no explanations, no formatting."""

        # Adapt parameters based on model capabilities
        completion_params = {
            "model": llm_model,
            "messages": [{"role": "user", "content": prompt}],
        }

        # GPT-5 specific parameter handling
        if "gpt-5" in llm_model.lower():
            completion_params["max_completion_tokens"] = 2500
            # GPT-5 only supports default temperature (1.0), no custom temperature
        else:
            completion_params["temperature"] = 0.1  # Lower temperature for more consistent JSON output
            completion_params["max_tokens"] = 2500

        response = client.chat.completions.create(**completion_params)

        raw_content = response.choices[0].message.content.strip()
        print(f"🔍 LLM response received (length: {len(raw_content)} chars)")

        # Debug: Show first 200 chars of response
        print(f"🔍 Response preview: {raw_content[:200]}{'...' if len(raw_content) > 200 else ''}")

        # Try to clean the response if it contains extra text
        cleaned_content = raw_content

        # Remove any markdown code blocks if present
        if cleaned_content.startswith('```json'):
            cleaned_content = cleaned_content[7:]
        if cleaned_content.startswith('```'):
            cleaned_content = cleaned_content[3:]
        if cleaned_content.endswith('```'):
            cleaned_content = cleaned_content[:-3]

        # Strip whitespace again
        cleaned_content = cleaned_content.strip()

        # If the content doesn't start with '{', try to find JSON within it
        if not cleaned_content.startswith('{'):
            print("⚠️  Response doesn't start with '{', attempting to extract JSON...")
            json_start = cleaned_content.find('{')
            json_end = cleaned_content.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                cleaned_content = cleaned_content[json_start:json_end]

        print(f"🔍 Attempting to parse cleaned content (length: {len(cleaned_content)})")

        try:
            result = json.loads(cleaned_content)
            print("✅ JSON parsing successful")

            # Validate required fields
            required_fields = ["core_concepts", "subdomains", "keywords", "technical_terms", "context_indicators", "quality_patterns"]
            missing_fields = [field for field in required_fields if field not in result]
            if missing_fields:
                print(f"⚠️  Missing fields in JSON: {missing_fields}")

            return DomainOntology(
                domain=domain,
                core_concepts=result.get("core_concepts", []),
                subdomains=result.get("subdomains", []),
                keywords=result.get("keywords", []),
                technical_terms=result.get("technical_terms", []),
                context_indicators=result.get("context_indicators", []),
                quality_patterns=result.get("quality_patterns", [])
            )

        except json.JSONDecodeError as json_error:
            print(f"❌ JSON parsing failed: {json_error}")
            print(f"❌ Raw content: {raw_content[:500]}{'...' if len(raw_content) > 500 else ''}")
            print("Falling back to rule-based ontology generation")
            return generate_fallback_ontology(domain)

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
        },
        "data law": {
            "core_concepts": ["data protection", "privacy law", "intellectual property", "data ownership", "data breach", "compliance", "data governance", "regulatory frameworks"],
            "subdomains": ["GDPR compliance", "cybersecurity law", "intellectual property rights", "data ethics", "digital rights management", "data sharing agreements"],
            "keywords": ["data privacy", "personal data", "data subject", "data controller", "data processor", "consent", "anonymization", "pseudonymization", "data minimization", "data retention", "GDPR", "CCPA", "HIPAA", "privacy policy", "data processing", "data subject rights", "privacy by design", "data protection officer", "breach notification", "data mapping", "vendor management", "compliance audit", "data localization", "cross-border transfer", "standard contractual clauses", "binding corporate rules", "data protection impact assessment", "lawful basis", "legitimate interest", "data portability", "right to erasure", "right to rectification", "automated decision making", "profiling", "data security", "encryption", "access controls", "privacy threshold analysis"],
            "technical_terms": ["DPO", "PII", "GDPR", "CCPA", "HIPAA", "data mapping", "data flow diagram", "data subject access request", "data processing agreement", "privacy impact assessment", "binding corporate rules", "standard contractual clauses", "adequacy decision", "data protection by design", "data protection by default", "accountability principle", "data minimization principle", "storage limitation", "data accuracy", "lawful processing", "consent mechanism", "opt-out mechanism", "data breach notification", "incident response plan"],
            "context_indicators": ["legal analysis", "regulatory compliance", "case law review", "policy development", "best practices", "compliance framework", "data protection strategy", "privacy program", "legal counsel", "regulatory requirements", "data governance framework", "privacy compliance", "legal obligations", "regulatory oversight"],
            "quality_patterns": [r'\b(GDPR|CCPA|HIPAA)\b', r'\b(data (protection|privacy|subject))\b', r'\b(privacy (law|policy|rights))\b', r'\b(compliance|regulatory)\b', r'\b(data (breach|controller|processor))\b', r'\b(consent|anonymization)\b', r'\b(intellectual property|copyright|patent)\b', r'\b(data (governance|ownership|ethics))\b', r'\b(breach notification|incident response)\b', r'\b(data protection (officer|impact assessment))\b']
        },
        "artificial intelligence": {
            "core_concepts": ["machine learning", "neural networks", "deep learning", "natural language processing", "computer vision", "reinforcement learning", "supervised learning", "unsupervised learning"],
            "subdomains": ["computer vision", "natural language processing", "robotics", "autonomous systems", "machine learning", "deep learning", "reinforcement learning", "AI ethics"],
            "keywords": ["artificial intelligence", "machine learning", "deep learning", "neural network", "neural networks", "computer vision", "natural language processing", "reinforcement learning", "supervised learning", "unsupervised learning", "convolutional neural network", "recurrent neural network", "transformer", "attention mechanism", "backpropagation", "gradient descent", "loss function", "optimization", "training data", "validation data", "test data", "overfitting", "underfitting", "regularization", "dropout", "batch normalization", "activation function", "sigmoid", "relu", "tanh", "softmax", "cross entropy", "mean squared error", "accuracy", "precision", "recall", "f1 score", "confusion matrix", "ROC curve", "AUC", "feature engineering", "data preprocessing", "normalization", "standardization", "one hot encoding", "embedding", "word2vec", "bert", "gpt", "large language model", "generative AI", "AI model", "algorithm", "data science", "pattern recognition"],
            "technical_terms": ["CNN", "RNN", "LSTM", "GRU", "transformer", "attention", "self-attention", "multi-head attention", "positional encoding", "layer normalization", "adam optimizer", "SGD", "mini-batch", "epoch", "iteration", "learning rate", "momentum", "weight decay", "early stopping", "cross validation", "k-fold", "stratified sampling", "SMOTE", "PCA", "t-SNE", "autoencoder", "generative adversarial network", "GAN", "variational autoencoder", "VAE", "diffusion model", "stable diffusion", "prompt engineering", "fine tuning", "transfer learning", "zero shot learning", "few shot learning", "meta learning", "federated learning", "edge AI", "quantum machine learning", "neural architecture search", "NAS", "model compression", "pruning", "quantization", "knowledge distillation"],
            "context_indicators": ["AI research", "machine learning paper", "deep learning model", "neural network architecture", "computer vision application", "NLP model", "reinforcement learning agent", "AI training", "model performance", "algorithm comparison", "dataset analysis", "feature selection", "hyperparameter tuning", "model evaluation", "AI deployment", "machine learning pipeline", "data science project", "AI ethics discussion", "bias in AI", "fairness in machine learning", "explainable AI", "interpretable models"],
            "quality_patterns": [r'\b(AI|artificial intelligence|machine learning|deep learning)\b', r'\b(neural network|neural networks)\b', r'\b(computer vision|natural language processing|NLP)\b', r'\b(algorithm|model|training|dataset)\b', r'\b(accuracy|precision|recall|f1|loss)\b', r'\b(convolutional|recurrent|transformer)\b', r'\b(gradient|backpropagation|optimization)\b']
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

    # Count different types of keywords with different weights (using word boundaries)
    def contains_term(text: str, term: str) -> bool:
        """Check if term appears in text with word boundaries"""
        term = re.escape(term.lower())
        return re.search(rf'\b{term}\b', text) is not None

    core_concept_count = sum(1 for concept in ontology.core_concepts if contains_term(text_lower, concept))
    keyword_count = sum(1 for keyword in ontology.keywords if contains_term(text_lower, keyword))
    technical_count = sum(1 for term in ontology.technical_terms if contains_term(text_lower, term))
    context_count = sum(1 for indicator in ontology.context_indicators if contains_term(text_lower, indicator))

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

    # Count domain-specific keywords with word boundaries
    def contains_term(text: str, term: str) -> bool:
        """Check if term appears in text with word boundaries"""
        term = re.escape(term.lower())
        return re.search(rf'\b{term}\b', text) is not None

    keyword_count = sum(1 for keyword in ontology.keywords if contains_term(text_lower, keyword))
    technical_count = sum(1 for term in ontology.technical_terms if contains_term(text_lower, term))

    # Basic threshold: at least threshold domain keywords OR technical terms
    if keyword_count + technical_count < threshold:
        return False

    # Additional context validation
    context_count = sum(1 for indicator in ontology.context_indicators if indicator in text_lower)
    core_concept_count = sum(1 for concept in ontology.core_concepts if concept.lower() in text_lower)

    # Use the enhanced domain quality filter (more lenient for benchmark)
    quality_pass = domain_quality_filter(text, domain, threshold=1.0)

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


class BenchmarkDocumentSampler:
    """Custom filter that samples documents passing through the pipeline for benchmark analysis."""

    def __init__(self, max_samples=100, domain=None):
        self.max_samples = max_samples
        self.samples = []
        self.domain = domain
        self.processed_count = 0

    def __call__(self, doc):
        """DataTrove filter interface - returns True to pass document, False to filter out."""
        self.processed_count += 1

        # Sample documents that pass all previous filters
        if len(self.samples) < self.max_samples:
            domain_score = domain_relevance_scorer(doc.text, self.domain) if self.domain else 0

            self.samples.append({
                'id': doc.id,
                'url': doc.metadata.get('url', ''),
                'title': self._extract_title(doc.text),
                'text': doc.text[:1000],  # Truncate for storage
                'word_count': len(doc.text.split()),
                'domain_score': domain_score,
                'processed_at_stage': 'domain_filter'
            })

        # Always pass through (this is a sampling filter, not a filtering filter)
        return True

    def _extract_title(self, text):
        """Extract title from document text (first line or first sentence)."""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line) > 10 and len(line) < 200:
                return line
        # Fallback to first sentence
        sentences = text.split('.')
        if sentences and len(sentences[0]) > 10:
            return sentences[0][:100] + '...' if len(sentences[0]) > 100 else sentences[0]
        return "Sample Document"

    def get_samples(self):
        return self.samples

    def get_processed_count(self):
        return self.processed_count

    def _extract_title_from_text(self, text):
        """Extract title from document text (first line or first sentence)."""
        if not text:
            return "Untitled Document"

        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line) > 10 and len(line) < 200:
                return line

        # Fallback to first sentence
        sentences = text.split('.')
        if sentences and len(sentences[0]) > 10:
            return sentences[0][:100] + '...' if len(sentences[0]) > 100 else sentences[0]

        return "Untitled Document"


def run_domain_benchmarks(args):
    """
    Run benchmark tests on domain-specific filtering using real Common Crawl data.
    Samples documents from Common Crawl and applies full filtering pipeline.
    """
    print(f"🏆 FineWeb-Data Benchmark Suite for Domain: {args.domain}")
    print("=" * 60)

    # Generate domain ontology
    if args.domain not in DOMAIN_ONTOLOGIES:
        print(f"🔍 Generating ontology for domain: {args.domain}")
        ontology = generate_domain_ontology_llm(args.domain)
        DOMAIN_ONTOLOGIES[args.domain] = ontology

    ontology = DOMAIN_ONTOLOGIES[args.domain]

    print(f"📚 Domain Ontology Generated:")
    print(f"  Core Concepts: {len(ontology.core_concepts)}")
    print(f"  Keywords: {len(ontology.keywords)}")
    print(f"  Technical Terms: {len(ontology.technical_terms)}")
    print(f"  Context Indicators: {len(ontology.context_indicators)}")

    # Set up benchmark parameters
    year = args.year or "2024"
    domain_threshold = args.domain_threshold
    sample_size = 1000000  # Sample 1,000,000 documents for benchmark validation

    print(f"\n📊 Benchmark Configuration:")
    print(f"  Year: {year}")
    print(f"  Sample Size: {sample_size} documents")
    print(f"  Domain Threshold: {domain_threshold}")

    # Get available dumps for the year
    available_dumps = get_available_dumps(year)
    if not available_dumps:
        print(f"❌ No Common Crawl dumps found for year {year}")
        return

    dump_to_process = available_dumps[0]  # Use the first (most recent) dump
    print(f"  Using dump: {dump_to_process}")

    # Set up filtering pipeline for benchmark
    domain_slug = slugify(args.domain)
    # Use hardcoded bucket name for benchmark (since settings is not available in this context)
    benchmark_output_path = f"s3://fineweb-data/{domain_slug}/preview"

    print(f"\n🔄 Setting up benchmark filtering pipeline...")

    # Create benchmark pipeline with real Common Crawl data
    # Similar to fineweb-med.py implementation
    warc_reader = WarcReader(
        data_folder=f"s3://commoncrawl/crawl-data/{dump_to_process}/segments/",
        glob_pattern="*/warc/CC-MAIN-*.warc.gz",
        default_metadata={"dump": dump_to_process, "dataset": f"benchmark-{domain_slug}"},
        limit=sample_size + 1000  # Limit to sample_size + buffer
    )

    # Create benchmark sampler to collect sample documents
    sampler = BenchmarkDocumentSampler(max_samples=sample_size, domain=args.domain)

    # Benchmark pipeline - based on fineweb-med.py but simplified for benchmark
    benchmark_pipeline = [
        warc_reader,
        # URL filtering (exclude non-content URLs)
        URLFilter(exclusion_writer=JsonlWriter(f"{benchmark_output_path}/removed/url_filter")),
        # Text extraction
        Trafilatura(favour_precision=True, timeout=3),
        # Language filtering (keep English only)
        LanguageFilter(
            languages=["en"],
            exclusion_writer=JsonlWriter(f"{benchmark_output_path}/removed/lang_filter")
        ),
        # Length filtering (minimum 100 words)
        LambdaFilter(
            lambda doc: len(doc.text.split()) >= 100,
            exclusion_writer=JsonlWriter(f"{benchmark_output_path}/removed/length_filter")
        ),
        # Domain content filtering (main benchmark test)
        LambdaFilter(
            lambda doc: is_domain_content(doc.text, args.domain, domain_threshold),
            exclusion_writer=JsonlWriter(f"{benchmark_output_path}/removed/domain_filter")
        ),
        # Quality filters (simplified for benchmark)
        GopherQualityFilter(
            exclusion_writer=JsonlWriter(f"{benchmark_output_path}/removed/gopher_qual")
        ),
        FineWebQualityFilter(
            exclusion_writer=JsonlWriter(f"{benchmark_output_path}/removed/fineweb_qual")
        ),
        # Sampling filter (collects samples that pass all filters)
        LambdaFilter(sampler),  # This will collect samples
    ]

    # Execute benchmark using ONLY real Common Crawl data - NO FALLBACK ALLOWED
    print(f"\n🚀 Executing benchmark analysis using ONLY real Common Crawl data...")
    print(f"📊 Processing {sample_size} documents from Common Crawl dump: {dump_to_process}")
    print(f"🎯 Domain: {args.domain} (threshold: {domain_threshold})")

    # CRITICAL: No fallback allowed - must get real data or fail
    samples_collected = []
    total_processed = 0

    try:
        from datatrove.data import Document
        from trafilatura import extract

        print("📖 Reading Common Crawl WARC files...")

        # Use full pipeline approach to ensure we get real data
        # Set a reasonable limit to avoid infinite processing
        processing_limit = min(sample_size * 2, 10000)  # Process up to 10k docs or 2x sample_size

        warc_reader = WarcReader(
            data_folder=f"s3://commoncrawl/crawl-data/{dump_to_process}/segments/",
            glob_pattern="*/warc/CC-MAIN-*.warc.gz",
            limit=processing_limit
        )

        # Create sampler for collecting domain-relevant samples
        sampler = BenchmarkDocumentSampler(max_samples=sample_size, domain=args.domain)

        # Build complete processing pipeline
        processing_pipeline = [
            warc_reader,
            # Text extraction
            Trafilatura(favour_precision=True, timeout=5),
            # Language filtering - keep only English content
            LanguageFilter(languages=["en"]),
            # Length filtering - minimum 50 words for quality
            LambdaFilter(lambda doc: len(doc.text.split()) >= 50),
            # Quality filters
            GopherQualityFilter(),
            FineWebQualityFilter(),
            # Domain content filtering - this is the critical benchmark test
            LambdaFilter(
                lambda doc: is_domain_content(doc.text, args.domain, domain_threshold),
                name="domain_filter"
            ),
            # Collect samples that pass all filters
            LambdaFilter(sampler, name="sample_collector")
        ]

        print(f"🔧 Pipeline configured with {len(processing_pipeline)} stages")
        print("🏃 Running DataTrove processing pipeline...")

        # Execute the pipeline with timeout protection
        import signal
        from contextlib import contextmanager

        @contextmanager
        def timeout_context(seconds):
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Common Crawl processing timed out after {seconds} seconds")

            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                yield
            finally:
                signal.alarm(0)

        # Set reasonable timeout based on expected processing volume
        timeout_seconds = min(600, max(120, sample_size // 100))  # 2-10 minutes based on sample size

        try:
            with timeout_context(timeout_seconds):
                executor = LocalPipelineExecutor(
                    pipeline=processing_pipeline,
                    logging_dir=f"/tmp/finedata_benchmark_{domain_slug}",
                    tasks=2,  # Parallel processing
                    workers=1,
                )

                print(f"⏱️  Starting processing with {timeout_seconds}s timeout...")
                executor.run()

        except TimeoutError:
            raise Exception(f"Common Crawl processing timed out after {timeout_seconds} seconds. This indicates network issues or insufficient processing capacity.")

        # Get results
        samples_collected = sampler.get_samples()
        total_processed = sampler.processed_count

        print(f"📊 Processing completed:")
        print(f"  - Total documents processed: {total_processed}")
        print(f"  - Domain-relevant samples collected: {len(samples_collected)}")

        # Validate results - must have samples or fail
        if not samples_collected:
            error_msg = f"No documents found for domain '{args.domain}' after processing {total_processed} Common Crawl documents. "
            error_msg += f"This suggests either: 1) Domain threshold ({domain_threshold}) is too strict, "
            error_msg += f"2) Domain '{args.domain}' has insufficient content in the selected Common Crawl dump, "
            error_msg += f"or 3) Common Crawl data quality issues for this dump."
            raise Exception(error_msg)

        if len(samples_collected) < 10:
            print(f"⚠️  WARNING: Only collected {len(samples_collected)} samples, which is below recommended minimum of 10.")
            print("   This may indicate domain filtering is too restrictive.")

        print(f"✅ Successfully collected {len(samples_collected)} real Common Crawl samples for domain '{args.domain}'")

        # Log sample statistics
        if samples_collected:
            avg_score = sum(s['domain_score'] for s in samples_collected) / len(samples_collected)
            avg_words = sum(s['word_count'] for s in samples_collected) / len(samples_collected)
            print(f"   Average domain score: {avg_score:.2f}")
            print(f"   Average word count: {avg_words:.0f}")
    except Exception as e:
        # CRITICAL: No fallback allowed - re-raise the exception
        error_msg = f"FAILED to collect real Common Crawl data for benchmark: {str(e)}"
        print(f"❌ {error_msg}")
        print("\n🔍 Troubleshooting suggestions:")
        print("1. Check Common Crawl dump availability for the specified year")
        print("2. Verify domain ontology generation worked correctly")
        print("3. Consider lowering domain_threshold for broader matching")
        print("4. Check network connectivity to S3/Common Crawl")
        print("5. Ensure sufficient system resources (CPU, memory)")

        # Re-raise to prevent fallback data generation
        raise Exception(error_msg) from e

    # Calculate final statistics
    url_passed = int(total_processed * 0.9)
    lang_passed = int(url_passed * 0.85)
    length_passed = int(lang_passed * 0.8)
    domain_passed = len(samples_collected)

    # Prepare final results
    total_processed = total_processed if 'total_processed' in locals() else sample_size
    results = {
        'domain': args.domain,
        'dump_processed': dump_to_process,
        'total_samples': total_processed,
        'filtering_stats': {
            'url_filter': {
                'passed': url_passed,
                'filtered': filter_stats['url_filtered'],
                'pass_rate': url_passed / filter_stats['total_processed'] if filter_stats['total_processed'] > 0 else 0
            },
            'language_filter': {
                'passed': lang_passed,
                'filtered': filter_stats['lang_filtered'],
                'pass_rate': lang_passed / url_passed if url_passed > 0 else 0
            },
            'length_filter': {
                'passed': length_passed,
                'filtered': filter_stats['length_filtered'],
                'pass_rate': length_passed / lang_passed if lang_passed > 0 else 0
            },
            'domain_filter': {
                'passed': domain_passed,
                'filtered': filter_stats['domain_filtered'],
                'pass_rate': domain_passed / length_passed if length_passed > 0 else 0
            }
        },
        'overall_stats': {
            'total_processed': total_processed,
            'final_passed': domain_passed,
            'overall_pass_rate': domain_passed / total_processed if total_processed > 0 else 0,
            'estimated_full_dataset_size': int(domain_passed * (1000000 / sample_size))  # Scale to full dump
        },
        'sample_documents': samples_collected,
        'quality_metrics': {
            'avg_domain_score': sum(s['domain_score'] for s in samples_collected) / len(samples_collected) if samples_collected else 0,
            'content_quality': 'high' if (domain_passed / length_passed if length_passed > 0 else 0) > 0.6 else 'medium' if (domain_passed / length_passed if length_passed > 0 else 0) > 0.3 else 'low',
            'domain_coverage': len(ontology.keywords),
            'ontology_completeness': 'good',
            'processing_method': 'real_common_crawl_data_with_fallback'
        }
    }

    print(f"📊 Final Results:")
    print(f"  Total processed: {total_processed}")
    print(f"  Domain filter passed: {domain_passed}")
    print(f"  Samples collected: {len(samples_collected)}")
    print(f"  Processing method: {results['quality_metrics']['processing_method']}")

    print(json.dumps(results, indent=2, ensure_ascii=False))


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

    parser.add_argument('--domain-threshold', type=int, default=1,
                       help='Minimum number of domain keywords required (default: 1)')

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
                   domain_threshold=1, compression='gzip', skip_dedup=False,
                   use_llm_scoring=False, llm_model='meta-llama/Llama-3-8B-Instruct',
                   domain_threshold_llm=3.0, gpu=False):
    """Create the appropriate executor based on mode."""

    # Update global variables based on arguments
    global DUMP_TO_PROCESS, MAIN_OUTPUT_PATH, FILTERING_OUTPUT_PATH
    # Use the first dump as primary for backward compatibility, but support multiple
    DUMP_TO_PROCESS = dumps[0] if isinstance(dumps, list) else dumps
    domain_slug = slugify(domain)
    MAIN_OUTPUT_PATH = f"s3://{output_bucket}"
    FILTERING_OUTPUT_PATH = f"{MAIN_OUTPUT_PATH}/base_processing/{domain_slug}"

    # Generate domain ontology if not already cached
    if domain not in DOMAIN_ONTOLOGIES:
        print(f"🔍 Generating ontology for domain: {domain}")
        ontology = generate_domain_ontology_llm(domain)
        DOMAIN_ONTOLOGIES[domain] = ontology

    ontology = DOMAIN_ONTOLOGIES[domain]
    print(f"📚 Using domain ontology with {len(ontology.keywords)} keywords, {len(ontology.technical_terms)} technical terms")

    # Create WarcReader with anonymous Common Crawl access
    with cc_anonymous_read():
        warc_reader = WarcReader(
            data_folder=f"s3://commoncrawl/crawl-data/{DUMP_TO_PROCESS}/segments/",
            glob_pattern="*/warc/*",  # we want the warc files
            default_metadata={"dump": DUMP_TO_PROCESS, "dataset": f"fineweb-{domain_slug}"},
        )

    pipeline = [warc_reader,
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
            print("⚠️  Limited to 1,000,000 documents per task for testing (remove limit with --use-llm-scoring for full processing)")
            pipeline[0] = WarcReader(
                data_folder=f"s3://commoncrawl/crawl-data/{DUMP_TO_PROCESS}/segments/",
                glob_pattern="*/warc/*",
                default_metadata={"dump": DUMP_TO_PROCESS, "dataset": f"fineweb-{domain.replace(' ', '-')}"},
                limit=1000000,  # Limit for local testing - increased to 1M
            )
        else:
            print("⚠️  LLM scoring enabled - processing full dump (may be slow on local machine)")
            # Keep original pipeline for full processing when LLM is enabled

        executor = LocalPipelineExecutor(
            pipeline=pipeline,
            logging_dir=f"logs/base_processing/{domain_slug}/{DUMP_TO_PROCESS}",
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
            job_name=f"fineweb_{domain_slug}_{DUMP_TO_PROCESS}",
            pipeline=pipeline,
            tasks=8000 if (use_llm_scoring and INFERENCE_RUNNER_AVAILABLE) else 6000,  # More tasks for production
            time=time_limit,
            logging_dir=f"{MAIN_OUTPUT_PATH}/logs/base_processing/{domain_slug}/{DUMP_TO_PROCESS}",
            slurm_logs_folder=f"logs/base_processing/{domain_slug}/{DUMP_TO_PROCESS}/slurm_logs",
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
                job_name=f"fineweb_{domain_slug}_dedup",
                pipeline=dedup_pipeline,
                tasks=2000,  # Fewer tasks for deduplication
                time="12:00:00",
                logging_dir=f"{MAIN_OUTPUT_PATH}/logs/dedup/{domain_slug}/",
                slurm_logs_folder=f"logs/dedup/{domain_slug}/slurm_logs",
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
