FROM python:3.10-slim

# ── System dependencies ──
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1 \
    curl \
    git \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# ── Create non-root user ──
# (Nginx needs root to start, so we'll adjust permissions)
RUN useradd -m -u 1000 user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# ── Install Python dependencies (cached layer) ──
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -r requirements.txt

# ── Pre-download PaddleOCR models during build ──
RUN python -c "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=True, lang='en')" || true

# ── Copy project files ──
COPY --chown=user . /app

# ── Setup Nginx ──
COPY nginx.conf /etc/nginx/nginx.conf
RUN touch /app/backend.log /app/streamlit.log && \
    chown -R user:user /app && \
    chmod +x /app/start.sh

# ── Build ChromaDB knowledge base ──
ENV BUILD_MODE=docker
RUN python scripts/build_knowledge_base.py || echo "WARNING: Knowledge base build had issues"

# Hugging Face Spaces port
EXPOSE 7860

# Start everything via script
CMD ["/bin/bash", "/app/start.sh"]