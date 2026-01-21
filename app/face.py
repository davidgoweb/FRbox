"""Face detection and embedding extraction module using face_recognition library."""
import numpy as np
import base64
from typing import Tuple, List
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


def decode_base64_image(image_data: str) -> np.ndarray:
    """Decode base64 encoded image to numpy array.

    Args:
        image_data: Base64 encoded image string

    Returns:
        Decoded image as numpy array (RGB format)

    Raises:
        ValueError: If image data is invalid or cannot be decoded
    """
    from io import BytesIO
    from PIL import Image

    # Remove data URL prefix if present
    if "," in image_data:
        image_data = image_data.split(",", 1)[1]

    # Decode base64
    image_bytes = base64.b64decode(image_data)

    # Load image using PIL (returns RGB format)
    image = Image.open(BytesIO(image_bytes))

    # Convert to numpy array (RGB)
    return np.array(image)


def resize_image(image: np.ndarray, max_width: int) -> np.ndarray:
    """Resize image maintaining aspect ratio.

    Args:
        image: Input image
        max_width: Maximum width for resized image

    Returns:
        Resized image
    """
    from PIL import Image

    height, width = image.shape[:2]

    if width <= max_width:
        return image

    scale = max_width / width
    new_height = int(height * scale)

    # Convert to PIL for resizing
    pil_img = Image.fromarray(image)
    resized = pil_img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    return np.array(resized)


def detect_face(image: np.ndarray) -> Tuple[int, int, int, int]:
    """Detect single face in image using face_recognition.

    Args:
        image: Input image (RGB format)

    Returns:
        Bounding box (top, right, bottom, left) of detected face

    Raises:
        ValueError: If no face detected or multiple faces detected
    """
    import face_recognition

    # Detect face locations (returns list of (top, right, bottom, left))
    face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=1)

    # Validate face count
    if len(face_locations) == 0:
        raise ValueError("No face detected in image")
    if len(face_locations) > settings.MAX_FACES:
        raise ValueError(f"Multiple faces detected ({len(face_locations)}). Only one face allowed.")

    # Return single face bounding box
    return face_locations[0]  # (top, right, bottom, left)


def extract_embedding(image: np.ndarray, face_bbox: Tuple[int, int, int, int]) -> np.ndarray:
    """Extract face embedding from image using face_recognition.

    Args:
        image: Input image (RGB format)
        face_bbox: Face bounding box (top, right, bottom, left)

    Returns:
        Face embedding vector (128-dim by default from face_recognition)
    """
    import face_recognition

    # Encode face (get embedding)
    # face_encodings returns a list of 128-dim embeddings
    embeddings = face_recognition.face_encodings(image, known_face_locations=[face_bbox])

    if len(embeddings) == 0:
        logger.warning("Failed to generate face embedding")
        return np.zeros(128, dtype=np.float32)

    return embeddings[0].astype(np.float32)
