#!/usr/bin/env python3
"""
Simple test script for FineWeb-Data ontology generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from finewebdata import generate_domain_ontology_llm, generate_fallback_ontology
from finewebdata import domain_relevance_scorer, domain_quality_filter, is_domain_content

def test_ontology_generation():
    """Test ontology generation for different domains"""
    print("🧪 Testing FineWeb-Data Ontology Generation")
    print("=" * 50)

    test_domains = ["education", "environment", "quantum computing", "finance"]

    for domain in test_domains:
        print(f"\n🔍 Testing domain: {domain}")

        try:
            # Test ontology generation
            ontology = generate_domain_ontology_llm(domain)

            print(f"  ✅ Ontology generated successfully")
            print(f"  📊 Core concepts: {len(ontology.core_concepts)}")
            print(f"  🔍 Keywords: {len(ontology.keywords)}")
            print(f"  🛠️  Technical terms: {len(ontology.technical_terms)}")
            print(f"  📝 Context indicators: {len(ontology.context_indicators)}")
            print(f"  🎯 Quality patterns: {len(ontology.quality_patterns)}")

            # Test sample content scoring
            sample_text = f"This is a comprehensive guide to {domain} principles and applications."
            score = domain_relevance_scorer(sample_text, domain)
            quality_pass = domain_quality_filter(sample_text, domain)
            content_pass = is_domain_content(sample_text, domain)

            print(f"  📈 Relevance score: {score:.2f}")
            print(f"  ✅ Quality filter: {'PASS' if quality_pass else 'FAIL'}")
            print(f"  ✅ Content filter: {'PASS' if content_pass else 'FAIL'}")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            print(f"  🔄 Falling back to rule-based ontology...")

            ontology = generate_fallback_ontology(domain)
            print(f"  ✅ Fallback ontology generated")
            print(f"  📊 Core concepts: {len(ontology.core_concepts)}")

def test_fallback_ontologies():
    """Test fallback ontology generation"""
    print("\n🧪 Testing Fallback Ontology Generation")
    print("=" * 40)

    test_domains = ["machine learning", "blockchain", "cybersecurity", "renewable energy"]

    for domain in test_domains:
        print(f"\n🔍 Testing fallback for: {domain}")

        ontology = generate_fallback_ontology(domain)

        print(f"  ✅ Generated {len(ontology.keywords)} keywords")
        print(f"  ✅ Generated {len(ontology.technical_terms)} technical terms")
        print(f"  ✅ Generated {len(ontology.context_indicators)} context indicators")

        # Test with sample content
        sample_text = f"Advanced {domain} techniques and methodologies."
        score = domain_relevance_scorer(sample_text, domain)
        print(f"  📈 Sample score: {score:.2f}")

if __name__ == "__main__":
    print("🚀 FineWeb-Data Test Suite")
    print("This script tests the ontology generation and scoring functionality.\n")

    # Test main ontology generation
    test_ontology_generation()

    # Test fallback ontologies
    test_fallback_ontologies()

    print("\n✅ All tests completed!")
    print("\n💡 Tips:")
    print("  - For full LLM-powered ontology generation, set OPENAI_API_KEY in .env")
    print("  - Fallback ontologies work for common domains without API calls")
    print("  - Run benchmark with: python finewebdata.py --domain education --benchmark")
