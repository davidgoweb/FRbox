"""Configuration for FRbox face recognition service."""
import os
from functools import lru_cache
from typing import List


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        # Image processing limits
        self.MAX_IMAGE_SIZE: int = int(os.getenv("MAX_IMAGE_SIZE", "2097152"))
        self.MAX_IMAGE_WIDTH: int = int(os.getenv("MAX_IMAGE_WIDTH", "640"))
        self.MAX_FACES: int = int(os.getenv("MAX_FACES", "1"))

        # Embedding settings
        self.EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "128"))
        self.SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))

        # Security settings
        # API keys - comma-separated list of valid keys (empty = no auth required for dev)
        api_keys_str = os.getenv("API_KEYS", "")
        self.API_KEYS: List[str] = [k.strip() for k in api_keys_str.split(",") if k.strip()]

        # CORS origins - comma-separated list of allowed origins (empty = allow all for dev)
        origins_str = os.getenv("ALLOWED_ORIGINS", "")
        self.ALLOWED_ORIGINS: List[str] = [o.strip() for o in origins_str.split(",") if o.strip()]

        # Rate limiting - requests per minute per API key
        self.RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

        # API settings
        self.API_TITLE: str = "FRbox API"
        self.API_VERSION: str = "1.0.0"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
