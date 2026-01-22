"""FRbox: Stateless face recognition service - Main FastAPI application."""
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.config import get_settings
from app.middleware import RequestSizeLimitMiddleware, LoggingMiddleware, APIKeyMiddleware, SecurityHeadersMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("=" * 50)
    logger.info("FRbox Face Recognition Service Starting")
    logger.info("=" * 50)
    logger.info(f"Version: {settings.API_VERSION}")
    logger.info(f"Embedding dimension: {settings.EMBEDDING_DIM}")
    logger.info(f"Similarity threshold: {settings.SIMILARITY_THRESHOLD}")
    logger.info(f"Max image width: {settings.MAX_IMAGE_WIDTH}")
    logger.info(f"Max faces: {settings.MAX_FACES}")

    # Security settings
    if settings.API_KEYS:
        logger.info(f"API key authentication: ENABLED ({len(settings.API_KEYS)} keys)")
    else:
        logger.warning("API key authentication: DISABLED (development mode)")
    if settings.ALLOWED_ORIGINS:
        logger.info(f"CORS origins: {settings.ALLOWED_ORIGINS}")
    else:
        logger.warning("CORS: Allowing all origins (development mode)")
    logger.info(f"Rate limit: {settings.RATE_LIMIT_PER_MINUTE} req/min per client")

    # Test face_recognition import
    try:
        import face_recognition
        logger.info("face_recognition library loaded successfully")
    except ImportError as e:
        logger.error(f"Failed to import face_recognition: {e}")
        logger.error("Install with: pip install face_recognition")
        raise

    logger.info("=" * 50)
    logger.info("FRbox service ready")
    logger.info("=" * 50)

    yield

    # Shutdown
    logger.info("FRbox service shutting down")


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Stateless face recognition microservice for embedding extraction and verification",
    lifespan=lifespan,
)

# Add CORS middleware - use settings or fallback to all origins for development
allowed_origins = settings.ALLOWED_ORIGINS if settings.ALLOWED_ORIGINS else ["*"]
logger.info(f"Setting up CORS with origins: {allowed_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,  # Set to False to avoid CORS preflight issues
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware (order matters - last added is executed first)
app.add_middleware(SecurityHeadersMiddleware)  # Applied first to response
app.add_middleware(APIKeyMiddleware)  # Validates API keys
app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# Include routes
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "frbox",
        "version": settings.API_VERSION
    }
