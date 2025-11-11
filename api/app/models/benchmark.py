"""
Benchmark job models
"""

from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class BenchmarkStatus(str, enum.Enum):
    """Benchmark job status enumeration."""
    QUEUED = "queued"
    RUNNING = "running"
    READY = "ready"
    FAILED = "failed"


class OrderStatus(str, enum.Enum):
    """Order status enumeration."""
    DRAFT = "draft"
    BENCHMARKING = "benchmarking"
    PREVIEW_READY = "preview_ready"
    AWAITING_PAYMENT = "awaiting_payment"
    PAID = "paid"
    CLUSTER_QUEUED = "cluster_queued"
    RUNNING = "running"
    FINALIZING = "finalizing"
    DELIVERED = "delivered"
    FAILED = "failed"


class BenchmarkJob(Base):
    """Benchmark job model for preview generation."""
    __tablename__ = "benchmark_jobs"

    id = Column(String, primary_key=True, index=True)
    domain = Column(String, nullable=False)
    keywords = Column(JSON, nullable=False)  # List of keywords
    languages = Column(JSON, nullable=False)  # List of languages
    time_range_start = Column(String, nullable=False)
    time_range_end = Column(String, nullable=False)
    quality_tier = Column(String, nullable=False)  # basic, standard, premium
    estimated_scale = Column(String, nullable=True)
    email = Column(String, nullable=False, index=True)

    status = Column(Enum(BenchmarkStatus), default=BenchmarkStatus.QUEUED)
    progress_pct = Column(Float, default=0.0)
    docs_read = Column(Integer, default=0)
    docs_kept = Column(Integer, default=0)
    tokens = Column(Integer, default=0)
    dedup_rate = Column(Float, default=0.0)

    # Quality metrics
    coverage = Column(Float, nullable=True)
    quality_pass_rate = Column(Float, nullable=True)
    pii_rate = Column(Float, nullable=True)
    toxicity_rate = Column(Float, nullable=True)
    lang_dist = Column(JSON, nullable=True)  # Language distribution
    domain_dist = Column(JSON, nullable=True)  # Domain distribution

    sample_url = Column(String, nullable=True)  # S3 URL for sample data
    suggested_params = Column(JSON, nullable=True)  # Suggested processing parameters

    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to order
    order = relationship("Order", back_populates="benchmark_job", uselist=False)


class Order(Base):
    """Order model for dataset generation."""
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    benchmark_job_id = Column(String, ForeignKey("benchmark_jobs.id"), nullable=False)
    quote_id = Column(String, nullable=True)  # Reference to quote used for pricing

    status = Column(Enum(OrderStatus), default=OrderStatus.DRAFT)

    # Pricing
    currency = Column(String, default="USD")
    subtotal = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    total = Column(Float, nullable=True)
    pricing_notes = Column(Text, nullable=True)

    # Live production stats (when running)
    fetched_docs = Column(Integer, default=0)
    filtered_docs = Column(Integer, default=0)
    deduped_docs = Column(Integer, default=0)
    final_tokens = Column(Integer, default=0)

    # Delivery
    hf_dataset_url = Column(String, nullable=True)
    dataset_card_url = Column(String, nullable=True)
    invoice_url = Column(String, nullable=True)

    # Stripe payment
    stripe_payment_intent_id = Column(String, nullable=True, unique=True)
    stripe_client_secret = Column(String, nullable=True)

    # SLURM cluster
    cluster_name = Column(String, nullable=True)
    slurm_job_id = Column(String, nullable=True)

    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    benchmark_job = relationship("BenchmarkJob", back_populates="order")

    # Timeline events
    timeline_events = relationship("OrderTimelineEvent", back_populates="order", order_by="OrderTimelineEvent.timestamp")


class OrderTimelineEvent(Base):
    """Timeline events for order status tracking."""
    __tablename__ = "order_timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String, nullable=False)  # Status change, payment, etc.
    description = Column(String, nullable=False)
    event_metadata = Column(JSON, nullable=True)  # Additional event data

    order = relationship("Order", back_populates="timeline_events")


class IdempotencyKey(Base):
    """Idempotency keys for preventing duplicate operations."""
    __tablename__ = "idempotency_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String, unique=True, index=True, nullable=False)
    operation = Column(String, nullable=False)  # e.g., "create_quote", "create_order"
    user_id = Column(String, nullable=True, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    response_data = Column(Text, nullable=False)  # JSON string of cached response
    created_at = Column(DateTime, default=datetime.utcnow)
