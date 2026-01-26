# FRbox - Stateless Face Recognition Tool

Stateless face recognition microservice for embedding extraction and verification.

## Features

- Face embedding extraction from images
- Face verification (1:1 comparison via cosine similarity)
- CPU-only
- Stateless - no data storage
- Docker-ready
- Horizontal-scaling friendly
- Horizontal-scaling friendly
- API key authentication
- Rate limiting
- CORS protection
- Security headers

## Quick Start

### Docker Compose (Easiest)

```bash
docker-compose up
```

### Docker (Manual)

```bash
docker build -t frbox .
docker run -p 8000:8000 frbox
```

The API will be available at `http://localhost:8000`

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default settings (dev mode: no auth, all CORS)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1

# Or with environment variables
export API_KEYS="your-api-key"
export ALLOWED_ORIGINS="http://localhost:8080"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

**Note**: `face_recognition` library requires dlib. On Ubuntu/Debian:
```bash
sudo apt-get install cmake g++ libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev
```

On macOS with Homebrew:
```bash
brew install cmake
```

### Using Environment File

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit with your settings
nano .env
```

Then run with Docker Compose (it will automatically load the `.env` file):
```bash
docker-compose up
```

## Testing

A web-based test interface is included in the `test/` directory:

```bash
# Serve the test interface
cd test
python -m http.server 8080
# Or use npx serve .
```

Then open `http://localhost:8080/index.html` in your browser.

**Test Interface Features:**
- Register faces and extract embeddings
- Verify face matches with adjustable threshold
- Configure API base URL and API key
- Connection status indicator
- Faces stored in browser localStorage (stateless client)

## API Documentation

Once running, visit:
- Interactive API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## Quick Reference

```bash
# Quick start (Docker)
docker-compose up

# Quick start (local)
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Generate API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Test health endpoint
curl http://localhost:8000/health

# Test embedding extraction
curl -X POST http://localhost:8000/embedding \
  -H "Content-Type: application/json" \
  -d '{"image_data": "base64_encoded_image"}'

# Test with API key
curl -X POST http://localhost:8000/embedding \
  -H "X-API-Key: your-key-here" \
  -H "Content-Type: application/json" \
  -d '{"image_data": "base64_encoded_image"}'
```

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

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "frbox",
  "version": "1.0.0"
}
```

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

## Configuration

Environment variables (see `.env.example`):

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

## Security

FRbox includes several security features to protect the service in production environments:

### Development vs Production Mode

The service runs in two modes based on configuration:

**Development Mode (default):**
- `API_KEYS` is empty → No authentication required
- `ALLOWED_ORIGINS` is empty → All origins allowed
- Suitable for local development and testing

**Production Mode:**
- `API_KEYS` is set → API key authentication enabled
- `ALLOWED_ORIGINS` is set → Only specified origins allowed
- Required for production deployments

### API Key Authentication

Protect your endpoints by requiring API keys. Set the `API_KEYS` environment variable with a comma-separated list of valid keys:

```bash
# Generate secure API keys
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in environment
export API_KEYS="key1,key2,key3"
```

Clients must include the key in the `X-API-Key` header:

```bash
curl -X POST http://localhost:8000/embedding \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"image_data": "..."}'
```

**Note**: If `API_KEYS` is empty (default), authentication is disabled for development.

### Rate Limiting

Prevent abuse with per-client rate limiting. Configure requests per minute:

```bash
export RATE_LIMIT_PER_MINUTE=60
```

Rate limiting is applied per API key (or per IP address if no API key is provided).

### CORS Protection

Restrict which origins can access your API:

```bash
export ALLOWED_ORIGINS="https://example.com,https://app.example.com"
```

**Note**: If `ALLOWED_ORIGINS` is empty (default), all origins are allowed for development.

### Security Headers

The following security headers are automatically added to all responses:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'none'`

### Input Validation

- **Image format validation**: Only JPEG, PNG, GIF, and WEBP formats are accepted (verified via magic bytes)
- **Base64 validation**: All base64 input is validated before decoding
- **Size limits**: Maximum image size is enforced via `MAX_IMAGE_SIZE`

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
├── test/
│   └── index.html     # Web-based test interface
│
├── .env.example       # Environment variables template
├── docker-compose.yml # Docker service configuration
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

## Performance

- Embedding extraction: ~100-200ms (CPU)
- Verification: <1ms
- Safe throughput: 2-5 requests/sec
- Memory usage: ~200-400MB

## Design Principles

- **Stateless**: No data persistence, memory-only processing (rate limiting per instance)
- **CPU-only**: No GPU dependencies (dlib CPU inference)
- **Single-face**: Images must contain exactly one face (enforced via MAX_FACES)
- **Horizontal-scaling**: Each instance is independent, no shared state required
- **Security-first**: Authentication, rate limiting, input validation, and security headers built-in
- **Development-friendly**: Defaults to open access for local testing, easy production hardening

## Docker Deployment

FRbox includes automated CI/CD via GitHub Actions for building and publishing Docker images to GitHub Container Registry (GHCR).

### Quick Pull and Run

```bash
# Pull the latest image
docker pull ghcr.io/davidgoweb/FRbox:latest

# Run with default settings
docker run -d --name frbox -p 8000:8000 ghcr.io/davidgoweb/FRbox:latest
```

### Using Docker Compose (Recommended)

An example docker-compose file for production deployment is provided:

```bash
# Copy the production example
cp .env.production.example .env

# Edit with your settings (API keys, CORS origins, etc.)
nano .env

# Start the service
docker compose -f docker-compose.production.yml --env-file .env up -d
```

### CI/CD Pipeline

The project includes a GitHub Actions workflow (`.github/workflows/docker-publish.yml`) that automatically:
- Builds Docker images on push to `main` branch
- Creates versioned tags when you create release tags (`v1.0.0`, etc.)
- Publishes to GitHub Container Registry (GHCR)

**For complete deployment guide, see [DEPLOYMENT.md](DEPLOYMENT.md)**

## License

MIT License - see LICENSE file for details.
