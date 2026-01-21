"""Configuration for FRbox face recognition service."""
import os
from functools import lru_cache


class Settings:
    """Application settings loaded from environment variables."""

    # Image processing limits
    MAX_IMAGE_SIZE: int = int(os.getenv("MAX_IMAGE_SIZE", "2097152"))  # 2MB in bytes
    MAX_IMAGE_WIDTH: int = int(os.getenv("MAX_IMAGE_WIDTH", "640"))
    MAX_FACES: int = int(os.getenv("MAX_FACES", "1"))

    # Embedding settings (face_recognition uses 128-dim by default)
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "128"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))

    # API settings
    API_TITLE: str = "FRbox API"
    API_VERSION: str = "1.0.0"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
