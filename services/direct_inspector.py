import time
import re
from urllib.parse import urlparse, urljoin
from html.parser import HTMLParser
from typing import Dict, Any, List, Optional
import requests
from config import Config

class HTMLSEOParser(HTMLParser):
    """
    Lightweight HTML parser using standard library to extract
    SEO, accessibility and metadata tags without requiring BeautifulSoup.
    """
    def __init__(self):
        super().__init__()
        self.title: Optional[str] = None
        self.in_title: bool = False
        self.meta_tags: List[Dict[str, str]] = []
        self.canonical_url: Optional[str] = None
        self.h1_tags: List[str] = []
        self.h2_tags: List[str] = []
        self.h3_tags: List[str] = []
        self.in_h1: bool = False
        self.in_h2: bool = False
        self.in_h3: bool = False
        self.current_h1: str = ""
        self.current_h2: str = ""
        self.current_h3: str = ""
        self.images_total: int = 0
        self.images_with_alt: int = 0
        self.images_missing_alt: int = 0
        self.has_viewport: bool = False
        self.viewport_content: str = ""
        self.has_doctype: bool = False

    def handle_decl(self, decl: str) -> None:
        if "html" in decl.lower():
            self.has_doctype = True

    def handle_starttag(self, tag: str, attrs: List[tuple]) -> None:
        attr_dict = {k.lower(): v for k, v in attrs if k}

        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            self.meta_tags.append(attr_dict)
            name = attr_dict.get("name", "").lower()
            if name == "viewport":
                self.has_viewport = True
                self.viewport_content = attr_dict.get("content", "")
        elif tag == "link":
            rel = attr_dict.get("rel", "").lower()
            if rel == "canonical":
                self.canonical_url = attr_dict.get("href")
        elif tag == "h1":
            self.in_h1 = True
            self.current_h1 = ""
        elif tag == "h2":
            self.in_h2 = True
            self.current_h2 = ""
        elif tag == "h3":
            self.in_h3 = True
            self.current_h3 = ""
        elif tag == "img":
            self.images_total += 1
            alt = attr_dict.get("alt")
            if alt is not None and alt.strip() != "":
                self.images_with_alt += 1
            else:
                self.images_missing_alt += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
            if self.current_h1.strip():
                self.h1_tags.append(self.current_h1.strip())
        elif tag == "h2":
            self.in_h2 = False
            if self.current_h2.strip():
                self.h2_tags.append(self.current_h2.strip())
        elif tag == "h3":
            self.in_h3 = False
            if self.current_h3.strip():
                self.h3_tags.append(self.current_h3.strip())

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title = (self.title or "") + data
        elif self.in_h1:
            self.current_h1 += data
        elif self.in_h2:
            self.current_h2 += data
        elif self.in_h3:
            self.current_h3 += data

def inspect_website_directly(url: str) -> Dict[str, Any]:
    """
    Directly performs HTTP/HTML checks on target website:
    - Measures Time to First Byte (TTFB)
    - Validates HTTPS, status code, redirects
    - Parses title, meta description, viewport, headings, alt tags
    - Probes robots.txt and sitemap.xml
    Returns structured audit data.
    """
    headers = {
        "User-Agent": "SitePulseAI/1.0 (Health Analyzer Bot; +https://sitepulse-ai.local)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    start_time = time.time()
    try:
        response = requests.get(url, headers=headers, timeout=Config.REQUEST_TIMEOUT, allow_redirects=True)
        ttfb_ms = round((time.time() - start_time) * 1000)
    except requests.exceptions.SSLError:
        return {"success": False, "error": "SSL Certificate verification failed for this website."}
    except requests.exceptions.Timeout:
        return {"success": False, "error": f"Connection timed out after {Config.REQUEST_TIMEOUT}s. Target server took too long to respond."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not establish connection to the domain. Verify the URL is correct and online."}
    except Exception as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}

    content_type = response.headers.get("Content-Type", "").lower()
    is_html = "text/html" in content_type or "application/xhtml" in content_type

    parser = HTMLSEOParser()
    if is_html:
        try:
            parser.feed(response.text[:500000])  # Parse first 500KB safely
        except Exception:
            pass

    # Meta description search
    meta_desc = None
    for meta in parser.meta_tags:
        if meta.get("name", "").lower() == "description":
            meta_desc = meta.get("content", "").strip()
            break

    # Check robots.txt
    robots_url = urljoin(url, "/robots.txt")
    has_robots = False
    try:
        robots_res = requests.get(robots_url, headers=headers, timeout=5)
        has_robots = robots_res.status_code == 200 and "user-agent" in robots_res.text.lower()
    except Exception:
        has_robots = False

    # Check sitemap.xml
    sitemap_url = urljoin(url, "/sitemap.xml")
    has_sitemap = False
    try:
        sitemap_res = requests.head(sitemap_url, headers=headers, timeout=5, allow_redirects=True)
        has_sitemap = sitemap_res.status_code == 200
    except Exception:
        has_sitemap = False

    is_https = url.lower().startswith("https://")
    status_code = response.status_code

    return {
        "success": True,
        "status_code": status_code,
        "ttfb_ms": ttfb_ms,
        "is_https": is_https,
        "title": parser.title.strip() if parser.title else None,
        "meta_description": meta_desc,
        "canonical_url": parser.canonical_url,
        "has_viewport": parser.has_viewport,
        "viewport_content": parser.viewport_content,
        "h1_tags": parser.h1_tags,
        "h2_tags": parser.h2_tags,
        "h3_tags": parser.h3_tags,
        "images_total": parser.images_total,
        "images_with_alt": parser.images_with_alt,
        "images_missing_alt": parser.images_missing_alt,
        "has_robots": has_robots,
        "has_sitemap": has_sitemap,
        "has_doctype": parser.has_doctype,
        "server": response.headers.get("Server", "Undisclosed"),
        "content_encoding": response.headers.get("Content-Encoding", "None"),
        "strict_transport_security": "strict-transport-security" in response.headers
    }
