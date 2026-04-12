FROM python:3.10-slim

# Install system dependencies + nginx
RUN apt-get update && apt-get install -y \
    nginx \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (HuggingFace requirement)
RUN useradd -m -u 1000 user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install Python dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download PaddleOCR models during build (so first boot isn't slow)
RUN python -c "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=True, lang='en')"

# Copy entire project
COPY --chown=user . /app

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Build ChromaDB knowledge base during Docker build
RUN python scripts/build_knowledge_base.py

# Make startup script executable
RUN chmod +x start.sh

EXPOSE 7860

CMD ["./start.sh"]