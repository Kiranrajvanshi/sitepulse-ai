# SitePulse AI — Website Health Analyzer

> **A production-ready, full-stack website performance, SEO, accessibility, and Core Web Vitals diagnostic platform.**  
> Built with **Python (Flask)**, **SQLite**, **Bootstrap 5**, **Chart.js**, and **Vanilla JavaScript**.  
> Designed for technical interviews and a standout LinkedIn portfolio showcase.

![SitePulse AI Banner](static/images/logo.svg)

---

## 🌟 Key Features

- ⚡ **Four Core Diagnostic Pillars**:
  - **Performance**: TTFB (Time to First Byte), render-blocking resources, payload compression.
  - **SEO Analysis**: Title tag evaluation, meta descriptions, heading structure (`H1`-`H6`), canonical tags, robots.txt, XML sitemaps, and mobile viewport compliance.
  - **Accessibility (WCAG 2.1 AA)**: Contrast ratios, image alt attributes, form labels, ARIA landmarks, and keyboard focus.
  - **Best Practices**: HTTPS enforcement, modern image format delivery (AVIF/WebP), HSTS, and valid HTML doctype.
- 🎯 **Core Web Vitals Telemetry**:
  - Direct tracking and scoring of **LCP**, **INP**, **CLS**, **FCP**, and **TTFB**.
  - Interactive **Chart.js Radar Benchmark** comparing the website against Google's "Good" thresholds.
- 🔄 **Dual Engine: Live PageSpeed API + Realistic Demo Mode**:
  - **Live Mode**: Connects directly to Google's official PageSpeed Insights v5 REST API with server-side API key protection.
  - **Demo Mode**: Deterministic, domain-specific evaluation when an API key is unconfigured or offline. Honest disclosure banner ensures transparency.
- 🔍 **Interactive Issue Explorer**:
  - Real-time client-side search by keyword.
  - Filtering by **Category** (*Performance*, *SEO*, *Accessibility*, *Best Practices*) and **Severity** (*Critical*, *High*, *Medium*, *Low*).
  - Detailed diagnostic modal revealing *The Problem*, *Why It Matters*, *Recommended Solution*, and *Expected Benefit*.
- 📊 **Audit History with SQLite Persistence**:
  - Stores audits with parameterized queries for SQL injection prevention.
  - Delete individual audits or clear history with a confirmation modal.
- 🖨️ **Print & PDF Export Ready**:
  - One-click print/save as PDF with dedicated `@media print` styling removing screen clutter.
- 🔗 **Web Share API with Clipboard Fallback**:
  - Native mobile sharing or clipboard URL copy with floating toast confirmation.
- 🌓 **Dark / Light Theme Toggle**:
  - Sleek dark navy default with smooth transitions and persistent `localStorage` preference.

---

## 🏗️ Architecture & Technology Stack

| Layer | Technology | Description |
|---|---|---|
| **Backend** | Python 3 + Flask | Modular routes, parameterized queries, and RESTful API endpoints. |
| **Database** | SQLite 3 | Embedded, zero-configuration database layer (`analyses` & `issues` tables). |
| **Frontend UI** | HTML5, CSS3, Bootstrap 5 | Custom SaaS design system, glassmorphism, responsive mobile layout. |
| **Visualizations** | Chart.js 4.x | Radar benchmark visualization for Core Web Vitals. |
| **Icons & Fonts** | Bootstrap Icons + Inter | Modern typography and vector iconography. |
| **External API** | Google PageSpeed Insights v5 | Official Lighthouse performance & CWV metrics. |

### Project Directory Structure

```
sitepulse-ai/
├── app.py                     # Flask application entry point and routes
├── config.py                  # Environment configuration and secrets management
├── requirements.txt           # Python dependencies (Flask, requests, python-dotenv, gunicorn)
├── .env.example               # Template for environment variables
├── .gitignore                 # Standard Python, SQLite, and IDE ignore rules
├── README.md                  # Detailed documentation & portfolio guide
├── DEPLOYMENT.md              # Production deployment instructions
│
├── database/
│   ├── __init__.py
│   ├── schema.sql             # SQL table definitions for analyses and issues
│   └── db.py                  # Parameterized SQLite queries & CRUD methods
│
├── services/
│   ├── __init__.py
│   ├── website_analyzer.py    # Main coordinator for website audits
│   ├── pagespeed_service.py   # Google PageSpeed Insights REST API client
│   ├── direct_inspector.py    # Direct HTTP & HTML DOM parser (standard library)
│   └── demo_data.py           # Realistic deterministic sample data for Demo Mode
│
├── static/
│   ├── css/
│   │   ├── style.css          # Core SaaS stylesheet (Navy/White, glassmorphism)
│   │   └── print.css          # Clean A4/Letter print & PDF export stylesheet
│   ├── js/
│   │   ├── main.js            # Theme toggling, toasts, clipboard helpers
│   │   ├── analyzer.js        # Multi-step progress animation & AJAX submission
│   │   ├── dashboard.js       # Chart.js radar, issue filtering, detail modal
│   │   └── history.js         # Audit history management & asynchronous deletion
│   └── images/
│       └── logo.svg           # Vector logo for SitePulse AI
│
└── templates/
    ├── base.html              # Core SaaS shell, sticky navbar, footer, modals
    ├── index.html             # Landing page with hero, features, workflow, benefits
    ├── report.html            # Results dashboard with circular score & issue table
    ├── history.html           # Historical audit archive
    ├── about.html             # Architecture, methodology, and tech stack details
    ├── printable_report.html  # Exportable print/PDF view
    ├── robots.txt             # Search engine crawler directives
    └── sitemap.xml            # XML sitemap for SEO
```

---

## 🚀 Quick Start: Run Locally in 3 Minutes

### Prerequisites
- **Python 3.9+** installed on your system.
- **Git** (optional).

### 1. Clone or Open the Project
```bash
git clone https://github.com/your-username/sitepulse-ai.git
cd sitepulse-ai
```

### 2. Create and Activate a Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example configuration file:
```bash
cp .env.example .env
```
*(On Windows PowerShell, use `copy .env.example .env`)*

Open `.env` in any text editor. If you do not have a PageSpeed API key yet, you can leave it blank; SitePulse AI will seamlessly operate in **Demo Mode**.

### 5. Launch the Application
```bash
python app.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🔑 How to Get a Free Google PageSpeed Insights API Key

1. Navigate to the [Google PageSpeed Insights API Documentation](https://developers.google.com/speed/docs/insights/v5/get-started).
2. Click the **"Get a Key"** button.
3. Select or create a Google Cloud Platform project.
4. Copy the generated API key.
5. Paste it into your `.env` file:
   ```env
   PAGESPEED_API_KEY=AIzaSyYourGeneratedGoogleApiKeyHere
   ```
6. Restart `app.py`. The application will now execute **Live Analyses** directly with official Google Lighthouse servers!

---

## 🧪 How Demo Mode vs. Live Mode Works

| Feature | Live Mode (`PAGESPEED_API_KEY` present) | Demo Mode (API Key absent or rate limited) |
|---|---|---|
| **Indicator** | Green badge: `Verified Live` | Amber banner: `Live analysis is unavailable. Showing sample analysis data.` |
| **Data Source** | Live Google PageSpeed API + direct HTTP probe | Realistic deterministic sample generator based on domain hash |
| **Honesty** | Fully real-time | Never pretends to be live; strictly disclosed |

---

## 🗄️ Database Setup & Migration

SitePulse AI uses an embedded SQLite database (`database/sitepulse.db`).
- The database and tables (`analyses` and `issues`) are **automatically created** on the first run of `app.py` via `init_db()`.
- All SQL queries use **parameterized statements (`?`)** to guard against SQL injection.
- The schema is designed for easy migration to PostgreSQL or MySQL simply by adjusting the connection string.

---

## 🚢 Deployment Guide

SitePulse AI is ready to deploy to any cloud provider that supports Python (Render, Railway, Fly.io, Heroku, AWS).

### Deploying to Render (Recommended Free Tier)
1. Push your code to a GitHub repository.
2. In [Render](https://render.com/), click **New +** -> **Web Service**.
3. Connect your repository.
4. Set the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Under **Environment Variables**, add:
   - `PAGESPEED_API_KEY` = `your_api_key` (optional)
   - `SECRET_KEY` = `random-secret-key`
6. Click **Deploy**. Your app will be live with a free SSL certificate!

---

## 💡 Key Architectural Talking Points for Interviews

- **No Frontend Bloat**: Clean HTML5/CSS3/Vanilla JS demonstrates strong command of core browser APIs, DOM manipulation, asynchronous fetch, and responsive design without relying on heavy frontend frameworks.
- **Service-Oriented Backend**: Business logic is decoupled from Flask routes into dedicated services (`pagespeed_service.py`, `direct_inspector.py`, `website_analyzer.py`), promoting unit testability and maintainability.
- **Ethical Software Design**: Clear disclosure between synthetic demo data and real API responses ensures transparency.
- **Defensive Engineering**: Sanitizes and normalizes user inputs, auto-prepends protocols, handles timeouts gracefully, and prevents SQL injection via parameterized statements.

---

## 📄 License
This project is open-source and available under the **MIT License**.
