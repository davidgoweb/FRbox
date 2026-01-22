"""API route definitions for FRbox."""
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict
import numpy as np
import logging
import time
import re
from collections import defaultdict

from app.face import decode_base64_image, resize_image, detect_face, extract_embedding
from app.similarity import verify_match
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# Simple in-memory rate limiter (stateless, per client)
_rate_limit_store: Dict[str, List[float]] = defaultdict(list)

def check_rate_limit(client_id: str) -> bool:
    """Check if client has exceeded rate limit."""
    now = time.time()
    minute_ago = now - 60

    # Clean old requests
    _rate_limit_store[client_id] = [
        req_time for req_time in _rate_limit_store[client_id]
        if req_time > minute_ago
    ]

    # Check limit
    if len(_rate_limit_store[client_id]) >= settings.RATE_LIMIT_PER_MINUTE:
        return False

    # Add current request
    _rate_limit_store[client_id].append(now)
    return True

def get_client_id(request: Request) -> str:
    """Get client identifier from API key or IP address."""
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"key:{api_key[:8]}"
    return f"ip:{request.client.host}"


class EmbeddingRequest(BaseModel):
    """Request for embedding extraction."""
    image_data: str = Field(..., description="Base64 encoded image", min_length=1)

    @field_validator('image_data')
    @classmethod
    def validate_base64(cls, v: str) -> str:
        """Validate base64 string format."""
        if not v or not v.strip():
            raise ValueError("image_data cannot be empty")

        # Remove data URL prefix if present
        data = v.split(",", 1)[1] if "," in v else v

        # Check if it's a valid base64 string (basic check)
        # Base64 strings contain only A-Z, a-z, 0-9, +, /, =, and whitespace
        if not re.match(r'^[A-Za-z0-9+/=\s]+$', data.strip()):
            raise ValueError("Invalid base64 format")

        return v


class EmbeddingResponse(BaseModel):
    """Response containing face embedding."""
    embedding: List[float]
    dim: int


class VerifyRequest(BaseModel):
    """Request for face verification."""
    embedding_a: List[float]
    embedding_b: List[float]
    threshold: float = Field(default=0.90, ge=0.0, le=1.0)


class VerifyResponse(BaseModel):
    """Response for face verification."""
    match: bool
    confidence: float


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: str


@router.post(
    "/embedding",
    response_model=EmbeddingResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 429: {"model": ErrorResponse}}
)
async def extract_embedding_endpoint(request: EmbeddingRequest, http_request: Request):
    """Extract face embedding from image.

    Accepts a base64-encoded image, detects the face, and returns the face embedding vector.

    - **image_data**: Base64 encoded image string (with or without data URL prefix)
    """
    # Apply rate limiting
    client_id = get_client_id(http_request)
    if not check_rate_limit(client_id):
        logger.warning(f"Rate limit exceeded for {client_id}")
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: Maximum {settings.RATE_LIMIT_PER_MINUTE} requests per minute"
        )

    start_time = time.time()

    try:
        # Decode image
        image = decode_base64_image(request.image_data)
        logger.debug(f"Image decoded: {image.shape}")

        # Resize if needed
        image = resize_image(image, settings.MAX_IMAGE_WIDTH)

        # Detect face
        face_bbox = detect_face(image)
        logger.debug(f"Face detected at: {face_bbox}")

        # Extract embedding
        embedding = extract_embedding(image, face_bbox)
        logger.debug(f"Embedding extracted: shape={embedding.shape}")

        # Log processing time
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"Embedding extraction completed in {elapsed:.1f}ms")

        return EmbeddingResponse(
            embedding=embedding.tolist(),
            dim=len(embedding)
        )

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail="Failed to process image")


@router.post(
    "/verify",
    response_model=VerifyResponse,
    responses={400: {"model": ErrorResponse}, 429: {"model": ErrorResponse}}
)
async def verify_face(request: VerifyRequest, http_request: Request):
    """Verify if two face embeddings match.

    Compares two face embeddings using cosine similarity and returns whether they match.

    - **embedding_a**: First face embedding vector (128 floats)
    - **embedding_b**: Second face embedding vector (128 floats)
    - **threshold**: Similarity threshold for match (default: 0.85)
    """
    # Apply rate limiting
    client_id = get_client_id(http_request)
    if not check_rate_limit(client_id):
        logger.warning(f"Rate limit exceeded for {client_id}")
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: Maximum {settings.RATE_LIMIT_PER_MINUTE} requests per minute"
        )

    start_time = time.time()

    try:
        # Validate embedding dimensions
        if len(request.embedding_a) != settings.EMBEDDING_DIM:
            raise HTTPException(
                status_code=400,
                detail=f"embedding_a must have {settings.EMBEDDING_DIM} dimensions, got {len(request.embedding_a)}"
            )
        if len(request.embedding_b) != settings.EMBEDDING_DIM:
            raise HTTPException(
                status_code=400,
                detail=f"embedding_b must have {settings.EMBEDDING_DIM} dimensions, got {len(request.embedding_b)}"
            )

        # Convert to numpy arrays
        emb_a = np.array(request.embedding_a, dtype=np.float32)
        emb_b = np.array(request.embedding_b, dtype=np.float32)

        # Verify match
        is_match, confidence = verify_match(emb_a, emb_b, request.threshold)

        # Log processing time
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"Verification completed in {elapsed:.2f}ms - match={is_match}, confidence={confidence:.3f}")

        return VerifyResponse(
            match=is_match,
            confidence=confidence
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying face: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify face")
