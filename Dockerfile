FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download PaddleOCR models during build
RUN python -c "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=True, lang='en')"

# Copy project files (no PDFs/images, they come from GitHub)
COPY --chown=user . /app

# Download legal PDFs from GitHub during build
RUN mkdir -p /app/data/legal_pdfs && \
    curl -L "https://github.com/Arjundas08/nyaya-setu/archive/refs/heads/main.tar.gz" \
    | tar xz --strip-components=3 \
    -C /app/data/legal_pdfs \
    "nyaya-setu-main/data/legal_pdfs/"

# Download images from GitHub
RUN curl -L "https://github.com/Arjundas08/nyaya-setu/raw/main/frontend/nyayasetu_logo.png" \
    -o /app/frontend/nyayasetu_logo.png 2>/dev/null || true && \
    curl -L "https://github.com/Arjundas08/nyaya-setu/raw/main/frontend/nyaya_setu_bridge.png" \
    -o /app/frontend/nyaya_setu_bridge.png 2>/dev/null || true && \
    curl -L "https://github.com/Arjundas08/nyaya-setu/raw/main/nyayasetu_bg.png" \
    -o /app/nyayasetu_bg.png 2>/dev/null || true

# Build ChromaDB from the downloaded PDFs
RUN python scripts/build_knowledge_base.py

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]