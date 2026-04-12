#!/bin/bash

# Start FastAPI backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit
streamlit run frontend/app.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false &

# Start Nginx
nginx -g "daemon off;"