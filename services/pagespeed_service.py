import logging
from typing import Dict, Any, Optional
import requests
from config import Config

logger = logging.getLogger("sitepulse.pagespeed")

def fetch_pagespeed_report(url: str) -> Optional[Dict[str, Any]]:
    """
    Queries Google PageSpeed Insights API v5.
    Returns normalized analysis data if successful, or None if the API fails or is unconfigured.
    """
    params = {
        "url": url,
        "strategy": "mobile",  # Standard mobile-first indexing
        "category": ["performance", "seo", "accessibility", "best-practices"]
    }
    
    if Config.PAGESPEED_API_KEY:
        params["key"] = Config.PAGESPEED_API_KEY

    try:
        response = requests.get(
            Config.PAGESPEED_API_ENDPOINT,
            params=params,
            timeout=Config.REQUEST_TIMEOUT + 15
        )
        
        if response.status_code != 200:
            logger.warning(f"PageSpeed API returned HTTP {response.status_code}: {response.text[:200]}")
            return None
            
        data = response.json()
        return parse_pagespeed_response(data, url)
        
    except requests.exceptions.Timeout:
        logger.warning(f"PageSpeed API timed out for URL: {url}")
        return None
    except Exception as e:
        logger.error(f"PageSpeed API call failed: {str(e)}")
        return None

def parse_pagespeed_response(raw: Dict[str, Any], url: str) -> Dict[str, Any]:
    """
    Parses Google PageSpeed API response into SitePulse AI schema.
    """
    lighthouse = raw.get("lighthouseResult", {})
    categories = lighthouse.get("categories", {})
    audits = lighthouse.get("audits", {})

    # 1. Category Scores (0-100)
    perf_score = int((categories.get("performance", {}).get("score") or 0.7) * 100)
    seo_score = int((categories.get("seo", {}).get("score") or 0.8) * 100)
    a11y_score = int((categories.get("accessibility", {}).get("score") or 0.8) * 100)
    bp_score = int((categories.get("best-practices", {}).get("score") or 0.8) * 100)
    overall_score = round((perf_score * 0.35) + (seo_score * 0.25) + (a11y_score * 0.20) + (bp_score * 0.20))

    # 2. Extract Core Web Vitals
    def get_audit_metric(audit_key: str, default_val: str, default_raw: float):
        a = audits.get(audit_key, {})
        val = a.get("displayValue", default_val)
        numeric = a.get("numericValue", default_raw)
        return val, numeric

    lcp_val, lcp_num = get_audit_metric("largest-contentful-paint", "2.5s", 2500)
    fcp_val, fcp_num = get_audit_metric("first-contentful-paint", "1.8s", 1800)
    cls_val, cls_num = get_audit_metric("cumulative-layout-shift", "0.05", 0.05)
    ttfb_val, ttfb_num = get_audit_metric("server-response-time", "300ms", 300)
    inp_val, inp_num = get_audit_metric("interaction-to-next-paint", "150ms", 150)

    # Convert numeric seconds
    lcp_sec = round(lcp_num / 1000.0, 2) if lcp_num > 50 else round(lcp_num, 2)
    fcp_sec = round(fcp_num / 1000.0, 2) if fcp_num > 50 else round(fcp_num, 2)
    cls_float = round(cls_num, 3)
    ttfb_int = round(ttfb_num)
    inp_int = round(inp_num)

    def eval_status(metric: str, value: float) -> str:
        if metric == "LCP":
            return "Good" if value <= 2.5 else ("Needs Improvement" if value <= 4.0 else "Poor")
        if metric == "INP":
            return "Good" if value <= 200 else ("Needs Improvement" if value <= 500 else "Poor")
        if metric == "CLS":
            return "Good" if value <= 0.1 else ("Needs Improvement" if value <= 0.25 else "Poor")
        if metric == "FCP":
            return "Good" if value <= 1.8 else ("Needs Improvement" if value <= 3.0 else "Poor")
        if metric == "TTFB":
            return "Good" if value <= 800 else ("Needs Improvement" if value <= 1800 else "Poor")
        return "Good"

    core_web_vitals = {
        "LCP": {
            "name": "Largest Contentful Paint",
            "value": f"{lcp_sec}s",
            "raw_value": lcp_sec,
            "unit": "s",
            "status": eval_status("LCP", lcp_sec),
            "explanation": "Measures loading performance: how quickly the main visual content renders on screen.",
            "suggestion": "Optimize hero images, compress media, and prioritize critical CSS delivery.",
            "benchmark": "< 2.5s (Good)"
        },
        "INP": {
            "name": "Interaction to Next Paint",
            "value": f"{inp_int}ms",
            "raw_value": inp_int,
            "unit": "ms",
            "status": eval_status("INP", inp_int),
            "explanation": "Measures page responsiveness to clicks, taps, and keyboard events.",
            "suggestion": "Break up long tasks in JavaScript and defer heavy tracking scripts.",
            "benchmark": "< 200ms (Good)"
        },
        "CLS": {
            "name": "Cumulative Layout Shift",
            "value": f"{cls_float}",
            "raw_value": cls_float,
            "unit": "",
            "status": eval_status("CLS", cls_float),
            "explanation": "Measures visual stability: unexpected layout shifts during page lifecycle.",
            "suggestion": "Set explicit width/height on all images, embeds, and dynamic banners.",
            "benchmark": "< 0.1 (Good)"
        },
        "FCP": {
            "name": "First Contentful Paint",
            "value": f"{fcp_sec}s",
            "raw_value": fcp_sec,
            "unit": "s",
            "status": eval_status("FCP", fcp_sec),
            "explanation": "Measures the time until the browser renders any text, image, or canvas element.",
            "suggestion": "Eliminate render-blocking CSS and enable HTTP/2 or HTTP/3 server compression.",
            "benchmark": "< 1.8s (Good)"
        },
        "TTFB": {
            "name": "Time to First Byte",
            "value": f"{ttfb_int}ms",
            "raw_value": ttfb_int,
            "unit": "ms",
            "status": eval_status("TTFB", ttfb_int),
            "explanation": "Measures server responsiveness to respond with the initial byte of HTML.",
            "suggestion": "Implement CDN edge caching and optimize server-side database queries.",
            "benchmark": "< 800ms (Good)"
        }
    }

    # Extract actionable issues from Lighthouse audits
    issues = []
    category_map = {
        "performance": "Performance",
        "seo": "SEO",
        "accessibility": "Accessibility",
        "best-practices": "Best Practices"
    }

    # Helper to parse audit items
    for audit_id, audit in audits.items():
        score = audit.get("score")
        if score is not None and score < 0.9:
            title = audit.get("title", audit_id)
            desc = audit.get("description", "")
            # Clean markdown links from description if any
            clean_desc = desc.split("[Learn more]")[0].strip()
            
            # Determine severity
            if score == 0 or (audit.get("scoreDisplayMode") == "binary" and score == 0):
                severity = "High" if "render-blocking" in audit_id or "viewport" in audit_id else "Medium"
                status = "Failed"
            else:
                severity = "Low"
                status = "Warning"

            # Determine category
            cat = "Performance"
            for c_id, c_data in categories.items():
                ref_audits = [r.get("id") for r in c_data.get("auditRefs", [])]
                if audit_id in ref_audits:
                    cat = category_map.get(c_id, "Performance")
                    break

            issues.append({
                "category": cat,
                "title": title,
                "description": clean_desc,
                "severity": severity,
                "impact": "High" if severity == "High" else "Medium",
                "status": status,
                "recommendation": f"Resolve {title} to improve your {cat} score.",
                "benefit": f"Optimizes {cat} metrics and elevates user experience."
            })

    # Sort issues by severity
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    issues.sort(key=lambda x: severity_order.get(x["severity"], 4))

    return {
        "is_demo": False,
        "overall_score": overall_score,
        "performance_score": perf_score,
        "seo_score": seo_score,
        "accessibility_score": a11y_score,
        "best_practices_score": bp_score,
        "metrics": core_web_vitals,
        "issues": issues[:15],  # Top 15 prioritized issues
        "summary": {
            "lighthouse_version": lighthouse.get("lighthouseVersion", "11.0"),
            "fetch_time": lighthouse.get("fetchTime"),
        }
    }
