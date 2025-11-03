#!/usr/bin/env python3
"""
Test ontology generation with improved prompt
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from finewebdata import generate_domain_ontology_llm

def test_single_domain():
    """Test ontology generation for a single domain"""
    domain = "education"

    print(f"🧪 Testing ontology generation for domain: {domain}")
    print("=" * 60)

    try:
        ontology = generate_domain_ontology_llm(domain)

        print("✅ Ontology generated successfully!")
        print(f"📊 Core concepts: {len(ontology.core_concepts)}")
        print(f"🔍 Keywords: {len(ontology.keywords)}")
        print(f"🛠️  Technical terms: {len(ontology.technical_terms)}")
        print(f"📝 Context indicators: {len(ontology.context_indicators)}")
        print(f"🎯 Quality patterns: {len(ontology.quality_patterns)}")

        # Show some examples
        print("\n📋 Sample content:")
        print(f"Core concepts: {ontology.core_concepts[:3]}")
        print(f"Keywords: {ontology.keywords[:5]}")
        print(f"Technical terms: {ontology.technical_terms[:3]}")
        print(f"Context indicators: {ontology.context_indicators[:3]}")
        print(f"Quality patterns: {ontology.quality_patterns[:2]}")

        return True

    except Exception as e:
        print(f"❌ Ontology generation failed: {e}")
        return False

if __name__ == '__main__':
    success = test_single_domain()
    if success:
        print("\n🎉 Ontology generation test passed!")
    else:
        print("\n❌ Ontology generation test failed!")
