"""
Configuration management for micro-SaaS product
Uses pydantic-settings for environment variable management

SHARED SERVICES (Auto-configured):
- S3 Storage: MinIO cluster (automatic bucket creation)
- PostgreSQL: Separate database per product
- Redis: Shared queues and caching
- Monitoring: Prometheus metrics (automatic scraping)
- Logging: Loki aggregation (automatic)
- SSL: Cert-manager TLS certificates (automatic)
- Payments: Stripe webhooks (shared endpoint)
"""
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    """Application settings with shared platform services"""
    
    # Application
    APP_NAME: str = "test-api"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    
    # API
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["*"]
    
    # =========================================================================
    # SHARED SERVICES - Auto-configured by platform
    # =========================================================================
    
    # PostgreSQL (Shared cluster, separate DB per product)
    # Database name is automatically set to APP_NAME
    POSTGRES_HOST: str = "postgresql.databases.svc.cluster.local"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "changeme"  # Override via secret
    POSTGRES_DB: str = "data-product"  # Auto-created on first connection
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis (Shared instance with namespaced keys)
    REDIS_HOST: str = "redis.databases.svc.cluster.local"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""  # Override via secret
    REDIS_DB: int = 0  # Use different DB numbers per product
    
    @property
    def REDIS_URL(self) -> str:
        """Construct Redis URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # MinIO S3 Storage (Shared cluster, separate bucket per product)
    S3_ENDPOINT: str = "http://minio.databases.svc.cluster.local:9000"
    S3_ACCESS_KEY: str = "minio-admin"  # Override via secret
    S3_SECRET_KEY: str = "changeme"  # Override via secret
    S3_BUCKET: str = "data-platform"  # Product-specific bucket
    S3_REGION: str = "us-east-1"  # MinIO default
    S3_USE_SSL: bool = False  # True in production with ingress
    
    # Celery (Uses Redis as broker and backend)
    @property
    def CELERY_BROKER_URL(self) -> str:
        """Celery broker URL (Redis DB 1)"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/1"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"
    
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        """Celery result backend (Redis DB 2)"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/2"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/2"
    
    # =========================================================================
    # MONITORING & OBSERVABILITY - Auto-configured
    # =========================================================================
    
    # Prometheus metrics (automatically scraped)
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 8000
    METRICS_PATH: str = "/metrics"
    
    # Logging (automatically shipped to Loki)
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # =========================================================================
    # PAYMENTS - Shared Stripe webhook endpoint
    # =========================================================================
    
    STRIPE_API_KEY: str = ""  # Override via secret
    STRIPE_WEBHOOK_SECRET: str = ""  # Override via secret
    STRIPE_WEBHOOK_PATH: str = "/webhooks/stripe"
    
    # Shared webhook endpoint (routes to product based on metadata)
    STRIPE_SHARED_WEBHOOK_URL: str = "https://webhooks.briggon.ai/stripe"
    
    # =========================================================================
    # FEATURE FLAGS
    # =========================================================================
    
    ENABLE_SWAGGER_UI: bool = True
    ENABLE_BACKGROUND_TASKS: bool = True
    ENABLE_RATE_LIMITING: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

