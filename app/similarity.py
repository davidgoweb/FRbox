"""Similarity calculation module for face verification."""
import numpy as np


def normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    """Normalize embedding vector to unit length.

    Args:
        embedding: Raw embedding vector

    Returns:
        Normalized embedding vector
    """
    norm = np.linalg.norm(embedding)
    if norm == 0:
        return embedding
    return embedding / norm


def cosine_similarity(embedding_a: np.ndarray, embedding_b: np.ndarray) -> float:
    """Calculate cosine similarity between two embeddings.

    Args:
        embedding_a: First embedding vector
        embedding_b: Second embedding vector

    Returns:
        Cosine similarity score (0 to 1, where 1 is identical)
    """
    # Normalize both embeddings
    a_normalized = normalize_embedding(embedding_a)
    b_normalized = normalize_embedding(embedding_b)

    # Calculate dot product (cosine similarity for normalized vectors)
    return float(np.dot(a_normalized, b_normalized))


def verify_match(
    embedding_a: np.ndarray,
    embedding_b: np.ndarray,
    threshold: float = 0.85
) -> tuple[bool, float]:
    """Verify if two embeddings match.

    Args:
        embedding_a: First embedding vector
        embedding_b: Second embedding vector
        threshold: Similarity threshold for match

    Returns:
        Tuple of (is_match, confidence_score)
    """
    confidence = cosine_similarity(embedding_a, embedding_b)
    is_match = confidence >= threshold
    return is_match, confidence
