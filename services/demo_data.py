import hashlib
from typing import Dict, Any, List
from urllib.parse import urlparse

def get_deterministic_score(seed: str, min_val: int, max_val: int) -> int:
    """Generates a stable pseudo-random integer between min_val and max_val based on string seed."""
    digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    num = int(digest[:6], 16)
    return min_val + (num % (max_val - min_val + 1))

def generate_demo_analysis(url: str) -> Dict[str, Any]:
    """
    Generates a realistic, deterministic demonstration health report for a website
    when live PageSpeed Insights API is unavailable or unconfigured.
    Clearly marks 'is_demo': True.
    """
    parsed = urlparse(url)
    domain = parsed.netloc or url.replace("https://", "").replace("http://", "").split("/")[0]
    
    # Deterministic scores based on domain seed
    perf_score = get_deterministic_score(domain + "_perf", 70, 88)
    seo_score = get_deterministic_score(domain + "_seo", 84, 96)
    a11y_score = get_deterministic_score(domain + "_a11y", 78, 92)
    bp_score = get_deterministic_score(domain + "_bp", 80, 94)
    overall_score = round((perf_score * 0.35) + (seo_score * 0.25) + (a11y_score * 0.20) + (bp_score * 0.20))
    
    # Core Web Vitals
    lcp_val = round(1.8 + (get_deterministic_score(domain + "_lcp", 0, 15) / 10.0), 2)  # 1.8s - 3.3s
    inp_val = get_deterministic_score(domain + "_inp", 110, 240)  # ms
    cls_val = round(0.02 + (get_deterministic_score(domain + "_cls", 0, 12) / 100.0), 3)  # 0.02 - 0.14
    fcp_val = round(1.1 + (get_deterministic_score(domain + "_fcp", 0, 14) / 10.0), 2)  # 1.1s - 2.5s
    ttfb_val = get_deterministic_score(domain + "_ttfb", 180, 480)  # ms

    def get_cwv_status(metric: str, value: float) -> str:
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
            "value": f"{lcp_val}s",
            "raw_value": lcp_val,
            "unit": "s",
            "status": get_cwv_status("LCP", lcp_val),
            "explanation": "Measures loading performance: how quickly the main content of the web page renders on screen.",
            "suggestion": "Optimize hero images, convert to WebP/AVIF, and prioritize critical CSS delivery.",
            "benchmark": "< 2.5s (Good)"
        },
        "INP": {
            "name": "Interaction to Next Paint",
            "value": f"{inp_val}ms",
            "raw_value": inp_val,
            "unit": "ms",
            "status": get_cwv_status("INP", inp_val),
            "explanation": "Measures page responsiveness: how quickly the page reacts to user clicks, taps, or key presses.",
            "suggestion": "Break up long-running JavaScript tasks and defer non-essential third-party analytics.",
            "benchmark": "< 200ms (Good)"
        },
        "CLS": {
            "name": "Cumulative Layout Shift",
            "value": f"{cls_val}",
            "raw_value": cls_val,
            "unit": "",
            "status": get_cwv_status("CLS", cls_val),
            "explanation": "Measures visual stability: unexpected layout shifts occurring while the page loads.",
            "suggestion": "Always include explicit width and height attributes on images and video elements.",
            "benchmark": "< 0.1 (Good)"
        },
        "FCP": {
            "name": "First Contentful Paint",
            "value": f"{fcp_val}s",
            "raw_value": fcp_val,
            "unit": "s",
            "status": get_cwv_status("FCP", fcp_val),
            "explanation": "Measures the time from navigation start until the browser renders the first piece of DOM content.",
            "suggestion": "Eliminate render-blocking stylesheets and enable server HTTP/2 compression.",
            "benchmark": "< 1.8s (Good)"
        },
        "TTFB": {
            "name": "Time to First Byte",
            "value": f"{ttfb_val}ms",
            "raw_value": ttfb_val,
            "unit": "ms",
            "status": get_cwv_status("TTFB", ttfb_val),
            "explanation": "Measures server responsiveness: the time it takes between request and receiving the initial byte.",
            "suggestion": "Implement CDN edge caching, optimize database queries, and reduce backend processing time.",
            "benchmark": "< 800ms (Good)"
        }
    }

    # Checklist breakdowns with honest statuses
    seo_checks = [
        {"name": "Page Title Tag", "status": "Passed", "details": f"Present and properly formatted: '{domain.capitalize()} - Home'"},
        {"name": "Meta Description", "status": "Passed", "details": "Found 155 character description optimized for search snippets."},
        {"name": "Heading Structure", "status": "Passed", "details": "Single H1 tag detected followed by hierarchical H2/H3 tags."},
        {"name": "Canonical URL Tag", "status": "Passed", "details": f"Points to canonical self-reference {url}"},
        {"name": "Robots.txt", "status": "Passed", "details": "Accessible and allows crawler indexing."},
        {"name": "XML Sitemap", "status": "Passed", "details": "Sitemap linked in robots.txt and responsive."},
        {"name": "Image Alt Attributes", "status": "Warning", "details": "2 out of 14 images are missing descriptive alt attributes."},
        {"name": "Mobile Viewport Tag", "status": "Passed", "details": "Configured with width=device-width, initial-scale=1.0."},
        {"name": "HTTPS Enforcement", "status": "Passed", "details": "All HTTP traffic automatically redirects to secure HTTPS."},
        {"name": "Structured Data (Schema.org)", "status": "Warning", "details": "Basic WebSite schema present; Organization schema recommended."}
    ]

    a11y_checks = [
        {"name": "Color Contrast Ratio", "status": "Warning", "details": "Secondary button text has a 3.8:1 contrast ratio (4.5:1 required by WCAG AA)."},
        {"name": "Image Alt Attributes", "status": "Warning", "details": "Decorative or informational images without alternative descriptions."},
        {"name": "Form Input Labels", "status": "Passed", "details": "All inputs have associated <label> or aria-label attributes."},
        {"name": "Logical Heading Hierarchy", "status": "Passed", "details": "Headings follow orderly h1 -> h2 -> h3 flow without skipped levels."},
        {"name": "ARIA Landmarks & Roles", "status": "Passed", "details": "<main>, <nav>, <header>, and <footer> semantic landmarks verified."},
        {"name": "Keyboard Navigability & Focus", "status": "Passed", "details": "Interactive elements display visible outline on tab navigation."}
    ]

    bp_checks = [
        {"name": "HTTPS Encryption", "status": "Passed", "details": "Valid SSL/TLS certificate installed with modern cipher suites."},
        {"name": "Console Errors", "status": "Passed", "details": "No uncaught exceptions logged to the browser console during render."},
        {"name": "Modern Image Formats", "status": "Warning", "details": "Certain legacy PNG/JPEG files could be served as modern AVIF/WebP."},
        {"name": "Valid HTML Doctype", "status": "Passed", "details": "<!DOCTYPE html> is declared at the start of document."},
        {"name": "Character Encoding", "status": "Passed", "details": "UTF-8 charset specified in <meta charset='utf-8'> tag."}
    ]

    # Prioritized Issues list
    issues: List[Dict[str, Any]] = [
        {
            "category": "Performance",
            "title": "Serve images in next-gen formats (AVIF / WebP)",
            "description": "Image formats like WebP and AVIF often provide better compression than PNG or JPEG, which means faster downloads and less data consumption.",
            "severity": "High",
            "impact": "High",
            "status": "Warning",
            "recommendation": "Convert hero banners and product imagery to modern WebP or AVIF formats using an image CDN or build pipeline.",
            "benefit": "Saves an estimated 420 KB of network payload and accelerates LCP by ~0.4s."
        },
        {
            "category": "Performance",
            "title": "Eliminate render-blocking resources",
            "description": "Resources are blocking the first paint of your page. Consider delivering critical JS/CSS inline and deferring non-critical scripts.",
            "severity": "Medium",
            "impact": "Medium",
            "status": "Warning",
            "recommendation": "Add defer or async attribute to third-party scripts and preload primary web fonts.",
            "benefit": "Improves First Contentful Paint (FCP) and reduces initial blank screen delay."
        },
        {
            "category": "Accessibility",
            "title": "Insufficient color contrast on secondary call-to-actions",
            "description": "Low-contrast text is difficult or impossible for many users with moderate visual impairments or bright ambient light to read.",
            "severity": "Medium",
            "impact": "Medium",
            "status": "Warning",
            "recommendation": "Adjust button text color or background darkness to achieve at least a 4.5:1 contrast ratio against the background.",
            "benefit": "Ensures WCAG 2.1 AA compliance and makes call-to-actions clearly legible."
        },
        {
            "category": "SEO",
            "title": "Missing descriptive image alt attributes",
            "description": "Image elements do not have [alt] attributes. Alt text helps search engine crawlers understand image content and assists screen reader users.",
            "severity": "Low",
            "impact": "Medium",
            "status": "Warning",
            "recommendation": "Add meaningful, contextual alt attributes to all informational images.",
            "benefit": "Improves Google Image Search indexing and universal accessibility."
        },
        {
            "category": "Best Practices",
            "title": "Explicit image dimensions missing",
            "description": "Some image elements lack explicit width and height attributes, leading to unexpected layout shifts as images load.",
            "severity": "Medium",
            "impact": "Medium",
            "status": "Warning",
            "recommendation": "Set explicit width and height attributes on <img> tags to reserve layout space ahead of load.",
            "benefit": "Reduces Cumulative Layout Shift (CLS) towards zero."
        }
    ]

    return {
        "url": url,
        "domain": domain,
        "is_demo": True,
        "overall_score": overall_score,
        "performance_score": perf_score,
        "seo_score": seo_score,
        "accessibility_score": a11y_score,
        "best_practices_score": bp_score,
        "metrics": core_web_vitals,
        "summary": {
            "seo_checks": seo_checks,
            "accessibility_checks": a11y_checks,
            "best_practices_checks": bp_checks,
            "server_headers": {
                "server": "Demo Web Server / CDN",
                "protocol": "HTTP/2",
                "content_type": "text/html; charset=UTF-8"
            }
        },
        "issues": issues
    }
