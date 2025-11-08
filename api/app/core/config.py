"""
Core configuration for FineData API
"""

import secrets
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator, ValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    """

    # Project
    PROJECT_NAME: str = "FineData API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    DEBUG: bool = False

    # Server
    SERVER_NAME: str = "FineData API"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        "http://54.159.47.120:23000",  # Current frontend deployment
        "https://finedata.example.com",  # Production frontend
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "finedata"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "finedata"
    POSTGRES_PORT: int = 5432
    DATABASE_URI: Optional[str] = None

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Database connection string."""
        if self.DATABASE_URI:
            return self.DATABASE_URI
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    @property
    def REDIS_URL(self) -> str:
        """Redis connection URL."""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_PRICE_ID: str = "price_dataset_generation"

    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_DEFAULT_REGION: str = "us-east-1"
    S3_BUCKET_DATASETS: str = "finedata-datasets"
    S3_BUCKET_SAMPLES: str = "finedata-samples"

    # Hugging Face
    HF_TOKEN: str = ""
    HF_ORG_NAME: Optional[str] = None

    # Email (SendGrid)
    SENDGRID_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@finedata.example.com"
    EMAIL_FROM_NAME: str = "FineData"

    # OpenAI (for ontology generation)
    OPENAI_API_KEY: str = ""

    # Celery
    CELERY_BROKER_URL: Optional[str] = None

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        """Celery result backend URL."""
        return self.REDIS_URL

    # Security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Benchmark settings
    BENCHMARK_SAMPLE_SIZE: int = 1000000  # 1M documents for preview
    MAX_BENCHMARK_CONCURRENT: int = 5

    # Production settings
    MAX_DATASET_SIZE_GB: int = 100
    SLURM_CLUSTER_NAME: str = "production-cluster"

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
