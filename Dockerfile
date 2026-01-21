FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for dlib/face_recognition
RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# No model files needed with face_recognition library
# It handles model loading automatically

EXPOSE 8000

# Run with single worker as specified
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
