import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if present
load_dotenv(BASE_DIR / ".env")

class Config:
    """
    Application Configuration for SitePulse AI.
    Handles environment variables with safe fallbacks.
    Supports local execution, traditional containers (Render/Railway),
    and serverless environments (Vercel).
    """
    SECRET_KEY = os.environ.get("SECRET_KEY", "sitepulse-ai-default-dev-secret-key-2025")
    
    # In serverless platforms (like Vercel), /tmp is the only writable directory
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        DATABASE_PATH = Path("/tmp") / "sitepulse.db"
    else:
        DATABASE_PATH = BASE_DIR / "database" / "sitepulse.db"
    
    # Google PageSpeed Insights API Key (optional)
    # If None or empty, the application gracefully activates Demo/Fallback Mode
    PAGESPEED_API_KEY = os.environ.get("PAGESPEED_API_KEY", "").strip()
    
    # PageSpeed API Endpoint
    PAGESPEED_API_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    # HTTP Request Timeout for external checks (in seconds)
    REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", 20))
    
    # Debug mode
    DEBUG = os.environ.get("FLASK_ENV", "development") == "development"
