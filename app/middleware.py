"""Middleware for request validation, limits, and security."""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware to validate API keys via X-API-Key header."""

    # Paths that don't require API key authentication
    EXEMPT_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next):
        """Validate API key if configured, otherwise exempt for development."""
        # Skip auth for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        # Skip auth for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # If no API keys configured, allow all (development mode)
        if not settings.API_KEYS:
            logger.debug("No API keys configured - allowing all requests")
            return await call_next(request)

        # Validate API key
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            logger.warning(f"Request missing API key: {request.client.host}")
            return JSONResponse(
                status_code=401,
                content={"error": "Unauthorized", "detail": "Missing X-API-Key header"}
            )

        if api_key not in settings.API_KEYS:
            logger.warning(f"Invalid API key from {request.client.host}")
            return JSONResponse(
                status_code=403,
                content={"error": "Forbidden", "detail": "Invalid API key"}
            )

        logger.debug(f"API key validated: {api_key[:8]}...")
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        """Add security headers to response."""
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'none'"

        return response


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
