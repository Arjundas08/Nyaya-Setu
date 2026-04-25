#!/bin/bash

# Port 7860 is the default for Hugging Face Spaces
echo "Starting Nyaya-Setu Services..."

# 1. Start FastAPI backend in background
echo "Launching FastAPI (Port 8000)..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

# 2. Start Streamlit in background
echo "Launching Streamlit (Port 8501)..."
streamlit run frontend/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false \
  --browser.usageStats false > streamlit.log 2>&1 &

# 3. Start Nginx in foreground (Port 7860)
echo "Launching Nginx Proxy (Port 7860)..."
nginx -g "daemon off;"