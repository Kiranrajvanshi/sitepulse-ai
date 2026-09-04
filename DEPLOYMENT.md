# Deployment Guide — SitePulse AI

This document provides step-by-step instructions to deploy **SitePulse AI** to popular cloud hosting platforms.

---

## 1. Deploying to Render.com (Recommended - Free Tier Available)

Render natively supports Flask applications using `gunicorn`.

### Steps:
1. Create a free account on [Render.com](https://render.com/).
2. Push your project to a GitHub or GitLab repository.
3. In Render Dashboard, click **New +** and select **Web Service**.
4. Choose **"Build and deploy from a Git repository"** and select your repo.
5. Fill in the deployment details:
   - **Name**: `sitepulse-ai`
   - **Region**: Select the region closest to your users.
   - **Branch**: `main`
   - **Root Directory**: Leave blank (root).
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
6. Add Environment Variables:
   - `PAGESPEED_API_KEY`: *(Optional)* Your Google PageSpeed Insights API key.
   - `SECRET_KEY`: A secure random string.
   - `FLASK_ENV`: `production`
7. Click **Create Web Service**.
8. Once built, your app will be live at `https://sitepulse-ai-xxxx.onrender.com`.

---

## 2. Deploying to Railway.app

Railway detects `requirements.txt` and automatically provisions a Python runtime.

### Steps:
1. Go to [Railway.app](https://railway.app/) and sign in with GitHub.
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your `sitepulse-ai` repository.
4. Add a `Procfile` (or specify in settings):
   ```
   web: gunicorn app:app --bind 0.0.0.0:$PORT
   ```
5. Set environment variables in the **Variables** tab (`PAGESPEED_API_KEY`, `SECRET_KEY`).
6. In **Settings** -> **Networking**, click **Generate Domain**.
7. Railway will deploy and provide your live HTTPS URL.

---

## 3. Deploying with Docker

If you prefer containerized deployment, create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=5000
EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2"]
```

Build and run the container:
```bash
docker build -t sitepulse-ai .
docker run -p 5000:5000 -e PAGESPEED_API_KEY="your_key" sitepulse-ai
```

---

## 4. Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `PAGESPEED_API_KEY` | No | `""` (Empty) | Google PageSpeed API key. If empty, runs in Demo Mode. |
| `SECRET_KEY` | Recommended | Built-in dev key | Secret key for Flask session signing. |
| `FLASK_ENV` | No | `development` | Set to `production` in live environments. |
| `PORT` | No | `5000` | Port for the web server. Automatically assigned by cloud hosts. |
