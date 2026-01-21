"""FRbox: Stateless face recognition service - Main FastAPI application."""
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.config import get_settings
from app.middleware import RequestSizeLimitMiddleware, LoggingMiddleware

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

# Add CORS middleware (allows opening test/index.html directly)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
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
