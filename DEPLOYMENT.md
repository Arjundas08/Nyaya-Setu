# 🚀 Nyaya-Setu Deployment Guide

## Your Resources
- **Domain:** nyayasetu.me (Namecheap, expires Mar 2027)
- **SSL:** PositiveSSL certificate (activate on Namecheap)
- **Hosting:** Microsoft Azure ($100 free credits from GitHub Student Pack)

---

## Option 1: Azure App Service (Recommended - Easiest)

### Step 1: Activate your Azure credits
1. Go to [azure.microsoft.com/free/students](https://azure.microsoft.com/free/students)
2. Sign in with your GitHub account
3. You'll get $100 Azure credits

### Step 2: Create Azure App Service
```bash
# Install Azure CLI (if not installed)
winget install Microsoft.AzureCLI

# Login to Azure
az login

# Create resource group
az group create --name nyayasetu-rg --location eastus

# Create App Service Plan (B1 = ~$13/month, fits in $100 credit)
az appservice plan create \
  --name nyayasetu-plan \
  --resource-group nyayasetu-rg \
  --sku B1 \
  --is-linux

# Create Web App for Backend
az webapp create \
  --name nyayasetu-api \
  --resource-group nyayasetu-rg \
  --plan nyayasetu-plan \
  --runtime "PYTHON:3.11"

# Create Web App for Frontend
az webapp create \
  --name nyayasetu-app \
  --resource-group nyayasetu-rg \
  --plan nyayasetu-plan \
  --runtime "PYTHON:3.11"
```

### Step 3: Set environment variables
```bash
# Backend env vars
az webapp config appsettings set \
  --name nyayasetu-api \
  --resource-group nyayasetu-rg \
  --settings \
    GROQ_API_KEY="your_groq_key" \
    GROQ_MODEL="llama-3.1-8b-instant" \
    MONGO_URI="your_mongo_uri" \
    INDIANKANOON_API_KEY="your_ik_key" \
    BHASHINI_USER_ID="your_bhashini_user" \
    BHASHINI_API_KEY="your_bhashini_key" \
    BHASHINI_INFERENCE_KEY="your_inference_key"
```

### Step 4: Deploy from GitHub
```bash
# Configure deployment from your GitHub repo
az webapp deployment source config \
  --name nyayasetu-api \
  --resource-group nyayasetu-rg \
  --repo-url https://github.com/Arjundas08/nyaya-setu \
  --branch main \
  --manual-integration
```

### Step 5: Add Custom Domain
1. Go to Azure Portal → App Services → nyayasetu-app
2. Settings → Custom domains → Add custom domain
3. Enter `nyayasetu.me`
4. Copy the TXT verification record
5. Add it to Namecheap DNS

---

## Option 2: Azure Container Instance (Docker)

```bash
# Build and push to Azure Container Registry
az acr create --name nyayasetuacr --resource-group nyayasetu-rg --sku Basic
az acr login --name nyayasetuacr

# Build image
docker build -t nyayasetuacr.azurecr.io/nyayasetu:latest .
docker push nyayasetuacr.azurecr.io/nyayasetu:latest

# Deploy container
az container create \
  --resource-group nyayasetu-rg \
  --name nyayasetu-container \
  --image nyayasetuacr.azurecr.io/nyayasetu:latest \
  --ports 8000 8501 \
  --cpu 2 \
  --memory 4
```

---

## Option 3: DigitalOcean Droplet ($6/month)

### Step 1: Create Droplet
1. Go to [digitalocean.com](https://digitalocean.com)
2. Create Droplet → Ubuntu 22.04 → Basic → $6/mo
3. Add SSH key

### Step 2: Setup server
```bash
ssh root@your_droplet_ip

# Update system
apt update && apt upgrade -y

# Install Python and dependencies
apt install python3.11 python3.11-venv python3-pip nginx certbot python3-certbot-nginx -y

# Clone repo
git clone https://github.com/Arjundas08/nyaya-setu.git
cd nyaya-setu

# Create venv and install
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env
nano .env  # Add your API keys

# Build ChromaDB
python scripts/build_knowledge_base.py
```

### Step 3: Create systemd services
```bash
# Backend service
cat > /etc/systemd/system/nyayasetu-backend.service << 'EOF'
[Unit]
Description=Nyaya-Setu Backend
After=network.target

[Service]
User=root
WorkingDirectory=/root/nyaya-setu
Environment="PATH=/root/nyaya-setu/venv/bin"
ExecStart=/root/nyaya-setu/venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Frontend service
cat > /etc/systemd/system/nyayasetu-frontend.service << 'EOF'
[Unit]
Description=Nyaya-Setu Frontend
After=network.target

[Service]
User=root
WorkingDirectory=/root/nyaya-setu
Environment="PATH=/root/nyaya-setu/venv/bin"
ExecStart=/root/nyaya-setu/venv/bin/streamlit run frontend/app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl daemon-reload
systemctl enable nyayasetu-backend nyayasetu-frontend
systemctl start nyayasetu-backend nyayasetu-frontend
```

### Step 4: Configure Nginx
```bash
cat > /etc/nginx/sites-available/nyayasetu << 'EOF'
server {
    listen 80;
    server_name nyayasetu.me www.nyayasetu.me;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/ {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

ln -s /etc/nginx/sites-available/nyayasetu /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### Step 5: Setup SSL (using your Namecheap PositiveSSL)
1. Activate SSL on Namecheap
2. Generate CSR on your server:
   ```bash
   openssl req -new -newkey rsa:2048 -nodes \
     -keyout /etc/nginx/ssl/nyayasetu.key \
     -out /etc/nginx/ssl/nyayasetu.csr
   ```
3. Submit CSR to Namecheap
4. Download certificate files
5. Update nginx config with SSL

---

## DNS Setup on Namecheap

Go to Namecheap → Domain List → nyayasetu.me → Manage → Advanced DNS

Add these records:
| Type | Host | Value | TTL |
|------|------|-------|-----|
| A | @ | your_server_ip | Automatic |
| A | www | your_server_ip | Automatic |
| CNAME | api | nyayasetu.me | Automatic |

---

## SSL Activation on Namecheap

1. Go to Namecheap → SSL Certificates → Activate
2. Select `HTTP-based` or `DNS-based` validation
3. For HTTP: Upload validation file to your server
4. For DNS: Add CNAME record as instructed
5. Download certificate bundle
6. Install on your server

---

## Verify Deployment

```bash
# Test backend
curl https://nyayasetu.me/api/

# Test frontend
curl https://nyayasetu.me/

# Test voice
curl https://nyayasetu.me/api/voice/status
```

---

## Cost Summary

| Option | Monthly Cost | Notes |
|--------|-------------|-------|
| Azure App Service B1 | ~$13 | Covered by $100 credit (7+ months free) |
| DigitalOcean Droplet | $6 | Basic 1GB RAM |
| Render.com | $7 | Per service |

**Recommendation:** Use Azure with your student credits - 7+ months free!

---

## Quick Commands Reference

```bash
# View logs
az webapp log tail --name nyayasetu-api --resource-group nyayasetu-rg

# Restart app
az webapp restart --name nyayasetu-api --resource-group nyayasetu-rg

# SSH into Azure App Service
az webapp ssh --name nyayasetu-app --resource-group nyayasetu-rg
```
