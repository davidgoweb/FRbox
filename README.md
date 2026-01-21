# FRbox

Stateless face recognition microservice for embedding extraction and verification.

## Features

- Face embedding extraction from images
- Face verification (1:1 comparison via cosine similarity)
- CPU-only
- Stateless - no data storage
- Docker-ready
- Horizontal-scaling friendly

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
pip install -r requirements.txt
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

## API Documentation

Once running, visit:
- Interactive API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### POST /embedding

Extract face embedding from a base64-encoded image.

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

### POST /verify

Verify if two face embeddings match.

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

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_IMAGE_SIZE` | 2097152 | Maximum image size in bytes (2MB) |
| `MAX_IMAGE_WIDTH` | 640 | Maximum image width for resizing |
| `MAX_FACES` | 1 | Maximum faces allowed in image |
| `EMBEDDING_DIM` | 128 | Output embedding dimension |
| `SIMILARITY_THRESHOLD` | 0.85 | Default verification threshold |

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
│   ├── main.py        # FastAPI app entry point
│   ├── api.py         # Route definitions
│   ├── face.py        # Face detection + embedding extraction
│   ├── similarity.py  # Cosine similarity calculation
│   ├── config.py      # Configuration management
│   └── middleware.py  # Request limits & logging
│
├── Dockerfile
├── requirements.txt
└── README.md
```

## Performance

- Embedding extraction: ~100-200ms (CPU)
- Verification: <1ms
- Safe throughput: 2-5 requests/sec
- Memory usage: ~200-400MB

## Design Principles

- **Stateless**: No data persistence, memory-only processing
- **CPU-only**: No GPU dependencies
- **Single-face**: Images must contain exactly one face
- **Horizontal-scaling**: Each instance is independent

## License

MIT License - see LICENSE file for details.
