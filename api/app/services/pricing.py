"""
Pricing service for dynamic quote calculation
"""

from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)


class PricingService:
    """Service for calculating dataset pricing based on requirements and quality metrics."""

    # Base pricing per million tokens
    BASE_PRICING = {
        "basic": 25.0,      # $25 per million tokens
        "standard": 50.0,   # $50 per million tokens
        "premium": 100.0,   # $100 per million tokens
    }

    # Quality tier multipliers
    QUALITY_MULTIPLIERS = {
        "basic": 0.8,
        "standard": 1.0,
        "premium": 1.5,
    }

    # Language complexity factors (relative to English)
    LANGUAGE_FACTORS = {
        "English": 1.0,
        "Spanish": 1.1,
        "French": 1.1,
        "German": 1.2,
        "Chinese": 1.8,
        "Japanese": 1.8,
        "Korean": 1.8,
        "Arabic": 2.0,
        "Russian": 1.3,
        "Portuguese": 1.1,
    }

    # Domain complexity factors
    DOMAIN_FACTORS = {
        "general": 1.0,
        "technical": 1.2,
        "scientific": 1.3,
        "medical": 1.5,
        "legal": 1.4,
        "financial": 1.3,
    }

    # Time range factors (newer content is more expensive)
    TIME_RANGE_FACTORS = {
        "2024-2025": 1.0,   # Current year - most expensive
        "2023-2024": 0.9,
        "2022-2023": 0.8,
        "2021-2022": 0.7,
        "2020-2021": 0.6,
        "2019-2020": 0.5,
        "2018-2019": 0.4,
    }

    def __init__(self):
        pass

    async def calculate_initial_quote(
        self,
        domain: str,
        keywords: list,
        languages: list,
        time_range: Dict[str, str],
        quality_tier: str,
        estimated_scale: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate initial quote based on user requirements."""

        try:
            # Estimate dataset size
            estimated_tokens = self._estimate_dataset_size(
                domain, keywords, languages, time_range, quality_tier, estimated_scale
            )

            # Calculate base price
            base_price_per_million = self.BASE_PRICING.get(quality_tier, self.BASE_PRICING["standard"])

            # Apply multipliers
            language_factor = self._calculate_language_factor(languages)
            domain_factor = self._calculate_domain_factor(domain)
            time_factor = self._calculate_time_factor(time_range)

            # Calculate subtotal
            adjusted_price_per_million = base_price_per_million * language_factor * domain_factor * time_factor
            subtotal = (estimated_tokens / 1_000_000) * adjusted_price_per_million

            # Calculate tax (8%)
            tax_rate = 0.08
            tax = subtotal * tax_rate
            total = subtotal + tax

            pricing_notes = self._generate_pricing_notes(
                estimated_tokens, quality_tier, language_factor, domain_factor, time_factor
            )

            return {
                "currency": "USD",
                "estimated_tokens": estimated_tokens,
                "subtotal": round(subtotal, 2),
                "tax": round(tax, 2),
                "total": round(total, 2),
                "pricing_notes": pricing_notes,
                "breakdown": {
                    "base_price_per_million": base_price_per_million,
                    "language_factor": language_factor,
                    "domain_factor": domain_factor,
                    "time_factor": time_factor,
                    "adjusted_price_per_million": round(adjusted_price_per_million, 2),
                }
            }

        except Exception as e:
            logger.error("Failed to calculate initial quote", error=str(e))
            # Return fallback pricing
            return self._get_fallback_pricing(quality_tier)

    def calculate_final_quote(
        self,
        benchmark_results: Dict[str, Any],
        quality_tier: str,
        languages: list,
        domain: str,
        time_range: Dict[str, str]
    ) -> Dict[str, Any]:
        """Calculate final quote based on actual benchmark results."""

        try:
            # Use actual token count from benchmark
            actual_tokens = benchmark_results.get("tokens", 0)

            # If no actual tokens, fall back to estimated
            if actual_tokens == 0:
                return self.calculate_initial_quote(
                    domain, [], languages, time_range, quality_tier
                )

            # Apply quality adjustments based on benchmark results
            quality_multiplier = self._calculate_quality_adjustment(benchmark_results)

            # Calculate base price
            base_price_per_million = self.BASE_PRICING.get(quality_tier, self.BASE_PRICING["standard"])

            # Apply multipliers
            language_factor = self._calculate_language_factor(languages)
            domain_factor = self._calculate_domain_factor(domain)
            time_factor = self._calculate_time_factor(time_range)

            # Calculate final price with quality adjustment
            adjusted_price_per_million = (
                base_price_per_million *
                language_factor *
                domain_factor *
                time_factor *
                quality_multiplier
            )

            subtotal = (actual_tokens / 1_000_000) * adjusted_price_per_million

            # Calculate tax (8%)
            tax_rate = 0.08
            tax = subtotal * tax_rate
            total = subtotal + tax

            pricing_notes = self._generate_final_pricing_notes(
                actual_tokens, benchmark_results, quality_multiplier
            )

            return {
                "currency": "USD",
                "actual_tokens": actual_tokens,
                "subtotal": round(subtotal, 2),
                "tax": round(tax, 2),
                "total": round(total, 2),
                "pricing_notes": pricing_notes,
                "quality_adjustment": quality_multiplier,
                "benchmark_results": benchmark_results,
            }

        except Exception as e:
            logger.error("Failed to calculate final quote", error=str(e))
            return self._get_fallback_pricing(quality_tier)

    def _estimate_dataset_size(
        self,
        domain: str,
        keywords: list,
        languages: list,
        time_range: Dict[str, str],
        quality_tier: str,
        estimated_scale: Optional[int] = None
    ) -> int:
        """Estimate the size of the dataset in tokens."""

        # Base estimate: 10 million tokens
        base_tokens = 10_000_000

        # Adjust based on user-provided scale estimate (number of documents)
        if estimated_scale and isinstance(estimated_scale, int):
            # Rough estimate: 500 tokens per document on average
            estimated_tokens = estimated_scale * 500

            # Adjust base tokens based on estimated size
            if estimated_tokens < 5_000_000:
                base_tokens = 5_000_000  # Minimum estimate
            elif estimated_tokens > 100_000_000:
                base_tokens = 100_000_000  # Maximum estimate
            else:
                base_tokens = estimated_tokens

        # Adjust based on quality tier (higher quality = fewer tokens kept)
        quality_adjustments = {
            "basic": 1.2,     # More lenient filtering = more tokens
            "standard": 1.0,
            "premium": 0.7,   # Stricter filtering = fewer tokens
        }

        quality_multiplier = quality_adjustments.get(quality_tier, 1.0)
        base_tokens *= quality_multiplier

        # Adjust based on language count (more languages = more tokens)
        language_multiplier = min(2.0, 0.8 + (len(languages) * 0.2))
        base_tokens *= language_multiplier

        # Adjust based on keyword count (more specific = fewer tokens)
        keyword_multiplier = max(0.5, 1.0 - (len(keywords) * 0.05))
        base_tokens *= keyword_multiplier

        return int(base_tokens)

    def _calculate_language_factor(self, languages: list) -> float:
        """Calculate language complexity factor."""

        if not languages:
            return 1.0

        # Average the complexity factors of all languages
        total_factor = 0
        valid_languages = 0

        for lang in languages:
            factor = self.LANGUAGE_FACTORS.get(lang, 1.0)
            total_factor += factor
            valid_languages += 1

        if valid_languages == 0:
            return 1.0

        return total_factor / valid_languages

    def _calculate_domain_factor(self, domain: str) -> float:
        """Calculate domain complexity factor."""

        domain_lower = domain.lower()

        # Check for domain keywords
        if any(word in domain_lower for word in ['medical', 'health', 'clinical', 'pharma']):
            return self.DOMAIN_FACTORS['medical']
        elif any(word in domain_lower for word in ['legal', 'law', 'contract', 'regulation']):
            return self.DOMAIN_FACTORS['legal']
        elif any(word in domain_lower for word in ['financial', 'banking', 'finance', 'trading']):
            return self.DOMAIN_FACTORS['financial']
        elif any(word in domain_lower for word in ['technical', 'programming', 'software', 'engineering']):
            return self.DOMAIN_FACTORS['technical']
        elif any(word in domain_lower for word in ['scientific', 'research', 'academic', 'physics', 'chemistry']):
            return self.DOMAIN_FACTORS['scientific']
        else:
            return self.DOMAIN_FACTORS['general']

    def _calculate_time_factor(self, time_range: Dict[str, str]) -> float:
        """Calculate time range factor."""

        try:
            start_year = int(time_range.get('start', '2024').split('-')[0])
            end_year = int(time_range.get('end', '2025').split('-')[0])

            # Use the more recent year for pricing
            recent_year = max(start_year, end_year)
            time_key = f"{recent_year}-{recent_year + 1}"

            return self.TIME_RANGE_FACTORS.get(time_key, 1.0)

        except (ValueError, KeyError):
            return 1.0

    def _calculate_quality_adjustment(self, benchmark_results: Dict[str, Any]) -> float:
        """Calculate price adjustment based on benchmark quality metrics."""

        coverage = benchmark_results.get('coverage', 0.5)
        quality_pass_rate = benchmark_results.get('quality_pass_rate', 0.8)
        pii_rate = benchmark_results.get('pii_rate', 0.01)

        # Higher coverage = lower price (easier to find content)
        coverage_factor = max(0.8, 1.2 - (coverage * 0.4))

        # Higher quality pass rate = premium pricing
        quality_factor = 0.9 + (quality_pass_rate * 0.2)

        # Higher PII rate = higher price (more processing needed)
        pii_factor = 1.0 + (pii_rate * 2.0)

        adjustment = coverage_factor * quality_factor * pii_factor

        # Keep adjustment within reasonable bounds
        return max(0.7, min(1.5, adjustment))

    def _generate_pricing_notes(
        self,
        estimated_tokens: int,
        quality_tier: str,
        language_factor: float,
        domain_factor: float,
        time_factor: float
    ) -> str:
        """Generate pricing explanation notes."""

        notes = []

        if estimated_tokens > 0:
            notes.append(f"Estimated dataset size: {estimated_tokens:,} tokens")

        notes.append(f"Quality tier: {quality_tier.title()}")

        if language_factor > 1.05:
            notes.append(f"Language complexity premium: +{(language_factor - 1) * 100:.0f}%")
        elif language_factor < 0.95:
            notes.append(f"Language complexity discount: -{(1 - language_factor) * 100:.0f}%")
        if domain_factor > 1.05:
            notes.append(f"Domain complexity premium: +{(domain_factor - 1) * 100:.0f}%")
        elif domain_factor < 0.95:
            notes.append(f"Domain complexity discount: -{(1 - domain_factor) * 100:.0f}%")

        if time_factor > 1.05:
            notes.append(f"Time range premium: +{(time_factor - 1) * 100:.0f}%")
        elif time_factor < 0.95:
            notes.append(f"Time range discount: -{(1 - time_factor) * 100:.0f}%")

        notes.append("Final price may vary based on actual processing results and quality metrics")

        return " | ".join(notes)

    def _generate_final_pricing_notes(
        self,
        actual_tokens: int,
        benchmark_results: Dict[str, Any],
        quality_adjustment: float
    ) -> str:
        """Generate final pricing explanation notes."""

        notes = []

        if actual_tokens > 0:
            notes.append(f"Actual dataset size: {actual_tokens:,} tokens")

        coverage = benchmark_results.get('coverage', 0)
        quality_rate = benchmark_results.get('quality_pass_rate', 0)

        if coverage > 0:
            notes.append(f"Coverage: {coverage:.1f}%")
        if quality_rate > 0:
            notes.append(f"Quality rate: {quality_rate:.1f}%")
        if quality_adjustment > 1.05:
            notes.append(f"Quality adjustment: +{(quality_adjustment - 1) * 100:.0f}%")
        elif quality_adjustment < 0.95:
            notes.append(f"Quality adjustment: -{(1 - quality_adjustment) * 100:.0f}%")
        return " | ".join(notes)

    def _get_fallback_pricing(self, quality_tier: str) -> Dict[str, Any]:
        """Return fallback pricing when calculation fails."""

        base_price = self.BASE_PRICING.get(quality_tier, self.BASE_PRICING["standard"])

        return {
            "currency": "USD",
            "estimated_tokens": 10_000_000,
            "subtotal": base_price,
            "tax": base_price * 0.08,
            "total": base_price * 1.08,
            "pricing_notes": "Default pricing - detailed calculation unavailable",
        }
