# SitePulse AI — Website Health Analyzer

> **A production-ready, full-stack website performance, SEO, accessibility, and Core Web Vitals diagnostic platform.**  
> Built with **Python (Flask)**, **SQLite**, **Bootstrap 5**, **Chart.js**, and **Vanilla JavaScript**.  
> Designed for technical interviews and a standout LinkedIn portfolio showcase.

![SitePulse AI Banner](static/images/logo.svg)

## 🌟 Key Features

- ⚡ **Four Core Diagnostic Pillars**: Performance, SEO, Accessibility, and Best Practices.
- 🎯 **Core Web Vitals Telemetry**: LCP, INP, CLS, FCP, and TTFB with Chart.js benchmarking.
- 🔄 **Dual Engine**: Live Google PageSpeed Insights API + clearly disclosed Demo Mode.
- 🔍 **Interactive Issue Explorer** with search and severity/category filters.
- 📊 **Audit History** with SQLite persistence and deletion controls.
- 🖨️ **Print & PDF Export Ready**.
- 🔗 **Web Share API with Clipboard Fallback**.
- 🌓 **Dark / Light Theme Toggle**.

## 🏗️ Architecture

| Layer | Technology |
|---|---|
| Backend | Python 3 + Flask |
| Database | SQLite 3 |
| Frontend UI | HTML5, CSS3, Bootstrap 5 |
| Visualizations | Chart.js 4.x |
| External API | Google PageSpeed Insights v5 |

## 🚀 Quick Start

```bash
git clone https://github.com/Kiranrajvanshi/sitepulse-ai.git
cd sitepulse-ai
python -m venv venv
# Windows PowerShell
.\\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

If no PageSpeed API key is configured, the application uses clearly labeled Demo Mode.

## 🗄️ Database

SQLite is initialized automatically on first run. Queries use parameterized statements to reduce SQL injection risk.

## 🚢 Deployment

The repository includes `render.yaml` for Render deployment with Gunicorn. See `DEPLOYMENT.md` for details.

## 📄 License

This project is open-source and available under the MIT License.
