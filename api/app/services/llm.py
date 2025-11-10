import json
import logging
from typing import Dict, Any, Optional
import openai
from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_ontology(self, domain: str, locale: str = "en") -> Dict[str, Any]:
        """
        Generate ontology for a given domain using GPT.
        """
        if not self.client:
            # Fallback to mock data if no API key
            logger.warning("OpenAI API key not configured, using mock data")
            return self._get_mock_ontology(domain, locale)

        try:
            prompt = self._build_ontology_prompt(domain, locale)
            # Use GPT-4-turbo for better performance (GPT-5 may not be available)
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert ontologist. Generate structured knowledge about domains for data curation. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.3
            )

            content = response.choices[0].message.content
            if content:
                try:
                    # Clean the response by removing markdown code blocks if present
                    content = content.strip()
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.endswith('```'):
                        content = content[:-3]
                    content = content.strip()

                    gpt_ontology = json.loads(content)

                    # Convert from finewebdata.py format to frontend expected format
                    ontology = self._convert_to_frontend_format(gpt_ontology, domain)
                    ontology["raw"] = {
                        "source": "gpt-4-turbo",
                        "confidence": 0.95,
                        "model": "gpt-4-turbo",
                        "tokens_used": response.usage.total_tokens if response.usage else None
                    }
                    logger.info(f"Generated ontology for domain: {domain} using GPT-4-turbo")
                    return ontology
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse GPT response as JSON: {content[:200]}... Error: {e}")
                    return self._get_mock_ontology(domain, locale)
            else:
                logger.error("Empty response from OpenAI")
                return self._get_mock_ontology(domain, locale)

        except Exception as e:
            logger.error(f"Failed to generate ontology with GPT: {str(e)}")
            return self._get_mock_ontology(domain, locale)

    def _build_ontology_prompt(self, domain: str, locale: str = "en") -> str:
        """Build the prompt for ontology generation based on finewebdata.py implementation."""
        language_instruction = ""
        if locale == "zh":
            language_instruction = "Please respond in Chinese for all text content."

        return f"""You are an expert ontologist specializing in domain knowledge representation. Your task is to create a comprehensive ontology for the domain "{domain}" that will be used for content filtering and dataset creation.

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

{language_instruction}

INSTRUCTIONS FOR CONTENT:
- core_concepts: 8 fundamental concepts that define the domain
- subdomains: 6 major sub-areas or specializations within the domain
- keywords: 40+ terms including general keywords, technical terms, phrases, and domain-specific language
- technical_terms: 20 specialized terms, jargon, acronyms specific to experts in the field
- context_indicators: 14 phrases that signal serious, professional discussion of the domain
- quality_patterns: 10 regex patterns (escaped with double backslashes) that identify high-quality content

REMEMBER: Respond ONLY with the JSON object. No additional text, no explanations, no formatting."""

    def _get_mock_ontology(self, domain: str, locale: str = "en") -> Dict[str, Any]:
        """Fallback mock ontology generation."""
        domain_lower = domain.lower().strip()

        # Mock ontology generation based on domain
        if "artificial intelligence" in domain_lower or "ai" in domain_lower:
            ontology = {
                "summary": "Artificial Intelligence encompasses the development of computer systems that can perform tasks that typically require human intelligence, including learning, reasoning, problem-solving, perception, and language understanding.",
                "concepts": ["Machine Learning", "Neural Networks", "Deep Learning", "Natural Language Processing", "Computer Vision", "Robotics", "Expert Systems"],
                "entities": ["OpenAI", "Google DeepMind", "Tesla", "Anthropic", "Meta AI", "Microsoft Research", "IBM Watson"],
                "intents": ["research development", "automation", "data analysis", "decision making", "content generation", "predictive modeling"],
                "positive_keywords": ["artificial intelligence", "machine learning", "neural network", "deep learning", "AI model", "algorithm", "automation"],
                "negative_keywords": ["manual", "human-only", "traditional", "static", "rule-based", "outdated"],
                "languages_suggested": ["English", "Chinese", "Python", "research papers"],
                "examples": [
                        {"title": "Recent Advances in Large Language Models", "url": "https://arxiv.org/abs/2307.09288"},
                        {"title": "Transformer Architecture Explained", "url": "https://arxiv.org/abs/1706.03762"},
                        {"title": "GPT-4 Technical Report", "url": "https://cdn.openai.com/papers/gpt-4.pdf"}
                    ],
                "raw": {"source": "mock", "confidence": 0.95}
            }
        elif "healthcare" in domain_lower or "medical" in domain_lower:
            ontology = {
                "summary": "Healthcare involves the prevention, diagnosis, and treatment of diseases, encompassing medical research, patient care, pharmaceuticals, and health policy.",
                "concepts": ["Diagnosis", "Treatment", "Prevention", "Pharmaceuticals", "Medical Devices", "Health Policy", "Patient Care"],
                "entities": ["WHO", "FDA", "Mayo Clinic", "Johns Hopkins", "Pfizer", "NIH", "CDC"],
                "intents": ["disease prevention", "treatment optimization", "drug development", "health policy", "patient outcomes", "medical research"],
                "positive_keywords": ["healthcare", "medical", "diagnosis", "treatment", "patient", "clinical", "pharmaceutical"],
                "negative_keywords": ["unhealthy", "disease", "illness", "injury", "complication", "side effect"],
                "languages_suggested": ["English", "Medical terminology", "Research papers"],
                "examples": [
                        {"title": "COVID-19 Vaccine Development", "url": "https://www.who.int/emergencies/diseases/novel-coronavirus-2019"},
                        {"title": "Advances in Cancer Treatment", "url": "https://www.cancer.gov"},
                        {"title": "Mental Health Research", "url": "https://www.nimh.nih.gov"}
                    ],
                "raw": {"source": "mock", "confidence": 0.92}
            }
        else:
            # Generic fallback ontology
            ontology = {
                "summary": f"{domain} represents a specialized domain requiring deep expertise and systematic knowledge organization.",
                "concepts": ["Research", "Analysis", "Methodology", "Best Practices", "Innovation", "Standards"],
                "entities": ["Industry Leaders", "Research Institutions", "Regulatory Bodies", "Professional Associations"],
                "intents": ["knowledge acquisition", "problem solving", "decision making", "optimization", "innovation"],
                "positive_keywords": [domain.lower(), "research", "analysis", "methodology", "best practices"],
                "negative_keywords": ["outdated", "inefficient", "problematic", "obsolete"],
                "languages_suggested": ["English", "Technical terminology"],
                "examples": [
                        {"title": f"Introduction to {domain}", "url": f"https://en.wikipedia.org/wiki/{domain.replace(' ', '_')}"},
                        {"title": f"{domain} Best Practices", "url": None},
                        {"title": f"Latest {domain} Developments", "url": None}
                    ],
                "raw": {"source": "mock", "confidence": 0.85}
            }

        return ontology

    def _convert_to_frontend_format(self, gpt_ontology: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """Convert from finewebdata.py format to frontend expected format."""
        # Create a summary from core concepts
        core_concepts_text = ", ".join(gpt_ontology.get("core_concepts", [])[:5])
        subdomains_text = ", ".join(gpt_ontology.get("subdomains", [])[:3])

        summary = f"{domain} represents a specialized domain encompassing {core_concepts_text}, with applications in {subdomains_text}."

        # Extract entities from technical terms (assuming they contain organization names)
        entities = []
        technical_terms = gpt_ontology.get("technical_terms", [])
        for term in technical_terms[:10]:  # Take first 10 technical terms as potential entities
            # Simple heuristic: terms that are all caps or contain common entity indicators
            if term.isupper() or any(word in term.upper() for word in ['INC', 'CORP', 'LTD', 'LLC', 'LAB', 'CENTER']):
                entities.append(term)

        # If no entities found, use some technical terms as entities
        if not entities:
            entities = technical_terms[:7]

        # Create intents from context indicators
        context_indicators = gpt_ontology.get("context_indicators", [])
        intents = []
        for indicator in context_indicators[:10]:
            # Convert context indicators to user intents
            if "academic" in indicator.lower():
                intents.append("academic research")
            elif "professional" in indicator.lower():
                intents.append("professional development")
            elif "research" in indicator.lower():
                intents.append("research and development")
            elif "practical" in indicator.lower():
                intents.append("practical application")
            elif "expert" in indicator.lower():
                intents.append("expert consultation")
            else:
                intents.append(indicator.replace("_", " "))

        # Use keywords as positive keywords, create negative keywords
        keywords = gpt_ontology.get("keywords", [])
        positive_keywords = keywords[:20]  # Take first 20 keywords

        # Generate negative keywords (opposite concepts)
        negative_keywords = [
            "outdated", "obsolete", "inefficient", "unreliable",
            "amateur", "beginner", "basic", "simplified",
            "incorrect", "misleading", "inaccurate", "flawed"
        ]

        # Suggest languages based on domain
        languages_suggested = ["English"]
        if "technical" in " ".join(keywords).lower():
            languages_suggested.extend(["Technical terminology", "Academic papers"])
        if len([k for k in keywords if not k.isascii()]) > 0:
            languages_suggested.append("Multiple languages")

        # Create examples from domain knowledge
        examples = [
            {"title": f"Introduction to {domain}", "url": f"https://en.wikipedia.org/wiki/{domain.replace(' ', '_')}"},
            {"title": f"{domain} Best Practices", "url": None},
            {"title": f"Latest {domain} Developments", "url": None}
        ]

        return {
            "summary": summary,
            "concepts": gpt_ontology.get("core_concepts", [])[:8],
            "entities": entities[:7],
            "intents": intents[:10],
            "positive_keywords": positive_keywords,
            "negative_keywords": negative_keywords,
            "languages_suggested": languages_suggested,
            "examples": examples
        }


# Global LLM service instance
llm_service = LLMService()
