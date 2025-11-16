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
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",
        "http://localhost:23000",  # Docker frontend
        "http://127.0.0.1:23000",  # Docker frontend
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

    # Database Connection Pool
    DB_POOL_SIZE: int = 20  # Maximum number of connections in the pool
    DB_MAX_OVERFLOW: int = 30  # Maximum number of connections that can be created beyond pool_size
    DB_POOL_RECYCLE: int = 3600  # Recycle connections after this many seconds (1 hour)
    DB_POOL_PRE_PING: bool = True  # Enable connection health checks

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
    S3_BUCKET_SAMPLES: str = "fineweb-data"

    # Hugging Face
    HF_TOKEN: str = ""
    HF_USERNAME: str = ""  # For dataset uploads
    HF_ORG_NAME: Optional[str] = None

    # Email (SendGrid)
    SENDGRID_API_KEY: str = ""
    EMAIL_FROM: str = "noreply@finedata.example.com"
    EMAIL_FROM_NAME: str = "FineData"

    # SMTP (alternative to SendGrid)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@finedata.ai"
    FROM_NAME: str = "FineData"

    # OpenAI (for ontology generation)
    OPENAI_API_KEY: str = ""

    # Moonshot AI (alternative LLM provider)
    MOONSHOT_API_KEY: str = ""

    # Frontend API URL (for Next.js)
    NEXT_PUBLIC_API_URL: str = "http://localhost:8000/api/v1"

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
    SLURM_NUM_NODES: int = 5  # Default number of EC2 t3.xlarge nodes
    SLURM_NODE_TYPE: str = "t3.xlarge"  # EC2 instance type for SLURM nodes

    # FineWebData Integration
    FINEDATA_SLURM_CONFIG_PATH: str = "/home/ubuntu/datatrove/finewebdata/config.yaml"
    FINEDATA_SLURM_SETUP_SCRIPT: str = "/home/ubuntu/datatrove/finewebdata/setup_slurm_cluster.sh"
    FINEDATA_HF_UPLOAD_SCRIPT: str = "/home/ubuntu/datatrove/finewebdata/publish_to_hf.sh"
    FINEDATA_BENCHMARK_SAMPLE_SIZE: int = 1000000
    FINEDATA_PRODUCTION_TIMEOUT_HOURS: int = 48

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
