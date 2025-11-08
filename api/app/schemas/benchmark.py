"""
Pydantic schemas for benchmark and order APIs
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr


class DomainFormData(BaseModel):
    """Form data for creating a benchmark job."""
    domain: str
    keywords: List[str]
    languages: List[str]
    time_range: Dict[str, str]  # {"start": "2020-01-01", "end": "2024-12-31"}
    quality_tier: str  # "basic", "standard", "premium"
    estimated_scale: Optional[str] = None
    email: EmailStr


class BenchmarkProgress(BaseModel):
    """Benchmark job progress information."""
    pct: float
    docs_read: int
    docs_kept: int
    tokens: int
    dedup_rate: float


class BenchmarkMetrics(BaseModel):
    """Benchmark job quality metrics."""
    coverage: float
    quality_pass_rate: float
    pii_rate: float
    toxicity_rate: float
    lang_dist: Dict[str, int]
    domain_dist: Dict[str, int]


class BenchmarkJobResponse(BaseModel):
    """Response for benchmark job status."""
    id: str
    status: str  # "queued", "running", "ready", "failed"
    progress: Optional[BenchmarkProgress] = None
    metrics: Optional[BenchmarkMetrics] = None
    sample_url: Optional[str] = None
    suggested_params: Optional[Dict] = None
    error: Optional[str] = None


class QuoteRequest(BaseModel):
    """Request for pricing quote."""
    jobId: str


class QuoteResponse(BaseModel):
    """Response with pricing information."""
    currency: str
    subtotal: float
    tax: float
    total: float
    pricing_notes: str


class CheckoutSessionRequest(BaseModel):
    """Request to create Stripe checkout session."""
    jobId: str
    plan: str = "one-off"


class CheckoutSessionResponse(BaseModel):
    """Response with Stripe client secret."""
    client_secret: str
    orderId: str


class OrderTimelineEvent(BaseModel):
    """Order timeline event."""
    timestamp: str
    label: str


class OrderResponse(BaseModel):
    """Order status response."""
    id: str
    status: str
    timeline: List[OrderTimelineEvent]
    live: Optional[Dict[str, int]] = None  # Production stats when running
    delivery: Optional[Dict[str, Optional[str]]] = None  # Delivery URLs
    error: Optional[str] = None


class BenchmarkJobCreateResponse(BaseModel):
    """Response for benchmark job creation."""
    jobId: str


class QuoteRequest(BaseModel):
    """Request for generating a quote."""
    domain: str
    keywords: List[str]
    languages: List[str]
    startDate: str  # YYYY-MM-DD
    endDate: str    # YYYY-MM-DD
    qualityTier: str  # "basic", "standard", "premium"
    estimatedScale: Optional[Dict[str, int]] = None  # {"docs": 100000} or {"tokens": 10000000}


class QuoteEstimate(BaseModel):
    """Quote price estimate range."""
    low: float
    high: float


class QuoteUnit(BaseModel):
    """Quote pricing unit information."""
    basis: str  # "per_million_pages"
    amount: float


class QuoteResponse(BaseModel):
    """Response for quote generation."""
    quoteId: str
    currency: str
    estimate: QuoteEstimate
    unit: QuoteUnit
    expiresAt: str  # ISO-8601 timestamp


class OrderCreateRequest(BaseModel):
    """Request for creating an order."""
    quoteId: str
    jobId: str
    email: EmailStr


class OrderCreateResponse(BaseModel):
    """Response for order creation."""
    orderId: str
    provider: str  # "stripe"
    clientSecret: str


class ProductionStatusResponse(BaseModel):
    """Response for production status."""
    status: str  # "initializing", "running", "dedup", "publishing", "delivered", "failed"
    estCompleteAt: Optional[str] = None  # ISO-8601 timestamp
    logsUrl: Optional[str] = None
    error: Optional[str] = None


# Email validation schemas
class EmailValidationRequest(BaseModel):
    """Request for email validation."""
    email: EmailStr


class EmailValidationResponse(BaseModel):
    """Response for email validation."""
    email: str
    isValid: bool
    domain: str
    checks: Dict[str, bool]


class EmailVerificationRequest(BaseModel):
    """Request for sending email verification."""
    email: EmailStr


class EmailVerificationConfirmRequest(BaseModel):
    """Request for confirming email verification."""
    token: str


# Ontology schemas
class OntologyExample(BaseModel):
    """Example content or page."""
    title: str
    url: Optional[str] = None


class OntologyResponse(BaseModel):
    """Response containing generated ontology."""
    summary: str
    concepts: Optional[List[str]] = None
    entities: Optional[List[str]] = None
    intents: Optional[List[str]] = None
    positive_keywords: Optional[List[str]] = None
    negative_keywords: Optional[List[str]] = None
    languages_suggested: Optional[List[str]] = None
    examples: Optional[List[OntologyExample]] = None
    raw: Optional[Dict[str, Any]] = None


class OntologyGenerateRequest(BaseModel):
    """Request to generate ontology for a domain."""
    domain: str
    locale: Optional[str] = 'en'
