"""Middleware for request validation and limits."""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce request size limits."""

    async def dispatch(self, request: Request, call_next):
        """Check request content-length before processing."""
        # Check content-length header
        content_length = request.headers.get("content-length")
        if content_length:
            size = int(content_length)
            if size > settings.MAX_IMAGE_SIZE:
                logger.warning(f"Request too large: {size} bytes")
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": "Request too large",
                        "detail": f"Maximum size is {settings.MAX_IMAGE_SIZE} bytes"
                    }
                )

        response = await call_next(request)
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests."""

    async def dispatch(self, request: Request, call_next):
        """Log request and response."""
        logger.info(f"{request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"{request.method} {request.url.path} - {response.status_code}")
        return response
