# FRbox - Stateless Face Recognition Tool

Stateless face recognition microservice for embedding extraction and verification.

## Features

### Core Functionality
- **Face Embedding Extraction** - Extract 128-dimensional face embeddings from images using state-of-the-art dlib face detection
- **Face Verification** - Compare two face embeddings using cosine similarity with configurable threshold
- **Single-Face Processing** - Designed for images containing exactly one face (enforced via `MAX_FACES` setting)

### Container & Deployment
- **Docker-First Design** - Pre-configured Dockerfile and docker-compose files for easy deployment
- **Multi-Stage Docker Build** - Optimized image size with production-ready base images
- **Containerized Dependencies** - All system dependencies included in the container
- **Horizontal Scaling** - Each container instance is independent, no shared state required
- **Health Check Endpoint** - Built-in container health monitoring for orchestration tools
- **Environment-Based Configuration** - Configure via environment variables or .env files

### Performance & Scalability
- **CPU-Only Operation** - No GPU dependencies, runs on any standard server
- **Stateless Architecture** - No data storage, memory-only processing
- **Lightweight Container** - ~200-400MB memory usage, 2-5 requests/sec safe throughput
- **Fast Processing** - Embedding extraction: ~100-200ms (CPU), Verification: <1ms

### Security Features
- **API Key Authentication** - Optional but recommended for production deployments
- **Rate Limiting** - Per-client request throttling (configurable per minute)
- **CORS Protection** - Restrict which origins can access your API
- **Security Headers** - Built-in protection against common web vulnerabilities
- **Input Validation** - Image format validation, base64 validation, size limits

### Developer Experience
- **Interactive API Docs** - Auto-generated Swagger UI and ReDoc documentation
- **Comprehensive Error Responses** - Clear error codes and messages for troubleshooting
- **Pre-built Images** - Available on GitHub Container Registry (GHCR)

## Quick Start

### Using Docker Compose (Recommended)

```bash
docker-compose up
```

The API will be available at `http://localhost:8000`

### Pull Pre-built Image

```bash
docker pull ghcr.io/davidgoweb/FRbox:latest
docker run -d --name frbox -p 8000:8000 ghcr.io/davidgoweb/FRbox:latest
```

### Build from Source

```bash
docker build -t frbox .
docker run -d --name frbox -p 8000:8000 frbox
```

### Using Environment File

```bash
# Copy the example file
cp .env.example .env

# Edit with your settings
nano .env

# Run with Docker Compose (automatically loads .env)
docker-compose up
```

## API Documentation

Once running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## API Endpoints

### POST /embedding

Extract face embedding from a base64-encoded image.

**Headers:**
```
X-API-Key: your-api-key-here  (required if API_KEYS configured)
Content-Type: application/json
```

**Request:**
```json
{
  "image_data": "base64_encoded_image_string"
}
```

**Response:**
```json
{
  "embedding": [0.123, -0.456, ...],
  "dim": 128
}
```

**Error Responses:**
- `401 Unauthorized` - Missing or invalid API key
- `413 Request Too Large` - Image exceeds MAX_IMAGE_SIZE
- `429 Too Many Requests` - Rate limit exceeded

### POST /verify

Verify if two face embeddings match.

**Headers:**
```
X-API-Key: your-api-key-here  (required if API_KEYS configured)
Content-Type: application/json
```

**Request:**
```json
{
  "embedding_a": [0.123, -0.456, ...],
  "embedding_b": [0.124, -0.455, ...],
  "threshold": 0.85
}
```

**Response:**
```json
{
  "match": true,
  "confidence": 0.91
}
```

**Error Responses:**
- `400 Bad Request` - Invalid embedding dimensions
- `401 Unauthorized` - Missing or invalid API key
- `429 Too Many Requests` - Rate limit exceeded

### GET /health

Health check endpoint for container orchestration and load balancer health checks.

**Response:**
```json
{
  "status": "healthy",
  "service": "frbox",
  "version": "1.0.0"
}
```

## Configuration

Configure the container via environment variables (see `.env.example`):

### Image Processing

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_IMAGE_SIZE` | 2097152 | Maximum image size in bytes (2MB) |
| `MAX_IMAGE_WIDTH` | 640 | Maximum image width for resizing |
| `MAX_FACES` | 1 | Maximum faces allowed in image |
| `EMBEDDING_DIM` | 128 | Output embedding dimension |
| `SIMILARITY_THRESHOLD` | 0.85 | Default verification threshold |

### Security

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEYS` | (empty) | Comma-separated list of valid API keys (empty = no auth) |
| `ALLOWED_ORIGINS` | (empty) | Comma-separated list of allowed CORS origins (empty = allow all) |
| `RATE_LIMIT_PER_MINUTE` | 60 | Requests per minute per API key or IP address |

### Passing Environment Variables

**Via Docker Compose:**
```yaml
services:
  frbox:
    environment:
      - API_KEYS=your-key-here
      - ALLOWED_ORIGINS=https://example.com
```

**Via Docker Run:**
```bash
docker run -d \
  -e API_KEYS=your-key-here \
  -e ALLOWED_ORIGINS=https://example.com \
  -p 8000:8000 \
  ghcr.io/davidgoweb/FRbox:latest
```

**Via .env File:**
```bash
docker-compose --env-file .env up
```

## Deployment

### Quick Pull and Run

```bash
# Pull the latest image
docker pull ghcr.io/davidgoweb/FRbox:latest

# Run with default settings (development mode: no auth, all CORS)
docker run -d --name frbox -p 8000:8000 ghcr.io/davidgoweb/FRbox:latest

# Check health
curl http://localhost:8000/health
```

### Production Deployment with Docker Compose

#### Step 1: Generate Secure API Keys

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Generate one or more keys and save them for configuration.

#### Step 2: Configure Environment Variables

```bash
# Copy the production example
cp .env.production.example .env

# Edit .env with production values
nano .env
```

Example `.env` configuration:
```env
# Security (REQUIRED for production!)
API_KEYS=your-generated-key-here,another-key-here
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Rate limiting
RATE_LIMIT_PER_MINUTE=60

# Image processing (adjust as needed)
MAX_IMAGE_SIZE=2097152
MAX_IMAGE_WIDTH=640
```

#### Step 3: Deploy with Docker Compose

```bash
# Start with environment file
docker compose -f docker-compose.production.yml --env-file .env up -d

# Check status
docker compose -f docker-compose.production.yml ps

# View logs
docker compose -f docker-compose.production.yml logs -f frbox
```

#### Step 4: Verify Deployment

```bash
# Health check
curl http://localhost:8000/health

# Test with API key
curl -X POST http://localhost:8000/embedding \
  -H "X-API-Key: your-generated-key-here" \
  -H "Content-Type: application/json" \
  -d '{"image_data": "base64_encoded_image"}'
```

### Security Configuration for Production

#### Authentication

For production, ALWAYS set `API_KEYS`:

```env
API_KEYS=key1,key2,key3
```

Clients must include the key:
```bash
curl -X POST http://localhost:8000/embedding \
  -H "X-API-Key: your-key-here" \
  -H "Content-Type: application/json" \
  -d '{"image_data": "..."}'
```

#### CORS Protection

Restrict which origins can access your API:

```env
ALLOWED_ORIGINS=https://example.com,https://app.example.com
```

#### Rate Limiting

Prevent abuse with per-client rate limits:

```env
RATE_LIMIT_PER_MINUTE=60
```

#### Security Headers

FRbox automatically includes:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'none'`

### Horizontal Scaling

FRbox is designed for horizontal scaling. Deploy multiple instances behind a load balancer:

```bash
# Scale to 3 instances
docker compose -f docker-compose.production.yml up -d --scale frbox=3
```

Each instance is completely independent and stateless, requiring no shared state or coordination.

### Container Resource Limits

Set resource limits for production deployments:

```yaml
services:
  frbox:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '2'
        reservations:
          memory: 512M
          cpus: '1'
```

### Container Health Checks

The Dockerfile includes a built-in health check:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

This enables automatic monitoring and restart by orchestration tools like Docker Swarm, Kubernetes, or ECS.


## Error Codes

| Status | Code | Description |
|--------|------|-------------|
| **400** | Bad Request | Invalid input (base64 format, image format, embedding dimensions) |
| **401** | Unauthorized | Missing or invalid API key |
| **403** | Forbidden | API key not authorized |
| **413** | Request Too Large | Image exceeds MAX_IMAGE_SIZE |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Processing error |

**Example Error Response:**
```json
{
  "error": "Unauthorized",
  "detail": "Missing X-API-Key header"
}
```

## How It Works

This service uses the [`face_recognition`](https://github.com/ageitgey/face_recognition) Python library, which:

- Uses dlib's state-of-the-art face detection
- Generates 128-dimensional face embeddings
- Downloads required models automatically on first run

No manual model setup needed!

## Architecture

```
frbox/
├── app/
│   ├── main.py        # FastAPI app entry point, CORS, middleware setup
│   ├── api.py         # Route definitions, rate limiting, validation
│   ├── face.py        # Face detection, embedding extraction, image validation
│   ├── similarity.py  # Cosine similarity calculation
│   ├── config.py      # Configuration management (env vars)
│   └── middleware.py  # API key auth, security headers, logging
│
├── .env.example       # Environment variables template
├── docker-compose.yml # Docker service configuration
├── docker-compose.production.yml  # Production Docker configuration
├── Dockerfile         # Container build instructions
├── requirements.txt   # Python dependencies
└── README.md
```

**Request Flow:**
```
Client Request
    ↓
CORS Middleware (preflight OPTIONS bypass auth)
    ↓
Security Headers Middleware
    ↓
API Key Middleware (exempts /health, /docs, OPTIONS)
    ↓
Request Size Limit Middleware
    ↓
Logging Middleware
    ↓
API Route Handler
    ↓
Rate Limiting Check (per API key or IP)
    ↓
Face Processing (decode → validate → detect → embed)
    ↓
Response (with security headers)
```

## Design Principles

- **Container-First**: Designed for Docker deployment with pre-configured images
- **Stateless**: No data persistence, memory-only processing (rate limiting per instance)
- **CPU-only**: No GPU dependencies (dlib CPU inference)
- **Single-face**: Images must contain exactly one face (enforced via MAX_FACES)
- **Horizontal-scaling**: Each instance is independent, no shared state required
- **Security-first**: Authentication, rate limiting, input validation, and security headers built-in

## License

MIT License - see LICENSE file for details.
