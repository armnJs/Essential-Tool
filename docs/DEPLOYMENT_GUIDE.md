# OmniConvert Production Deployment Guide 🚀

OmniConvert is fully configured for zero-downtime, production-grade cloud deployment across all major hosting platforms.

---

## 🌟 Option 1: Render (Free & 1-Click Recommended)

1. Sign up / log in to [Render.com](https://render.com).
2. Click **New +** ➔ **Web Service**.
3. Connect your GitHub repository: `https://github.com/armnJs/Essential-Tool.git`.
4. Render will automatically detect `render.yaml` or set:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server.py:app --host 0.0.0.0 --port $PORT`
5. Click **Create Web Service**. Your live URL will be active in ~2 minutes!

---

## 🚀 Option 2: Railway.app

1. Go to [Railway.app](https://railway.app).
2. Click **New Project** ➔ **Deploy from GitHub repo**.
3. Select `armnJs/Essential-Tool`.
4. Railway detects `Procfile` and `requirements.txt` automatically.
5. Click **Deploy**.

---

## 🐳 Option 3: Docker (Any Container Host)

Build and run locally or on any cloud server (AWS, GCP, DigitalOcean, Azure):

```bash
# Build container image
docker build -t omniconvert .

# Run container on port 8000
docker run -d -p 8000:8000 --name omniconvert-app omniconvert
```

Access at `http://localhost:8000`.

---

## ⚡ Option 4: Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Run `vercel` in your project folder.
3. Vercel will use `vercel.json` and deploy automatically.
