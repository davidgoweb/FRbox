"""API route definitions for FRbox."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
import numpy as np
import logging
import time

from app.face import decode_base64_image, resize_image, detect_face, extract_embedding
from app.similarity import verify_match
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


class EmbeddingRequest(BaseModel):
    """Request for embedding extraction."""
    image_data: str = Field(..., description="Base64 encoded image")


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
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def extract_embedding_endpoint(request: EmbeddingRequest):
    """Extract face embedding from image.

    Accepts a base64-encoded image, detects the face, and returns the face embedding vector.

    - **image_data**: Base64 encoded image string (with or without data URL prefix)
    """
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
    responses={400: {"model": ErrorResponse}}
)
async def verify_face(request: VerifyRequest):
    """Verify if two face embeddings match.

    Compares two face embeddings using cosine similarity and returns whether they match.

    - **embedding_a**: First face embedding vector (128 floats)
    - **embedding_b**: Second face embedding vector (128 floats)
    - **threshold**: Similarity threshold for match (default: 0.85)
    """
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
