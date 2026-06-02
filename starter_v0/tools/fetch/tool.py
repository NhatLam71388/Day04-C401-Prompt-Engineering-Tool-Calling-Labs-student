from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err


import re

def read_url(url: str = "") -> dict[str, Any]:
    try:
        key = os.getenv("FIRECRAWL_API_KEY")
        if key:
            response = requests.post(
                "https://api.firecrawl.dev/v1/scrape",
                json={"url": url, "formats": ["markdown"]},
                headers={"Authorization": f"Bearer {key}"},
                timeout=60,
            )
            response.raise_for_status()
            data = response.json().get("data", {})
            meta = data.get("metadata", {}) or {}
            return {"tool": "read_url", "url": url, "items": [{
                "title": meta.get("title") or url,
                "url": meta.get("sourceURL") or url,
                "source": domain(url),
                "summary": (data.get("markdown") or "")[:4000],
            }]}
            
        # FREE FALLBACK: Basic requests get
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        response.raise_for_status()
        html = response.text
        
        # Super simple tag stripping
        text = re.sub(r'<style.*?>.*?</style>', '', html, flags=re.DOTALL)
        text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Extract basic title if possible
        title = url
        title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            
        return {"tool": "read_url", "url": url, "items": [{
            "title": title,
            "url": url,
            "source": domain(url),
            "summary": text[:4000], # Keep first 4000 chars to avoid prompt overflow
        }], "note": "Sử dụng Basic Scraper miễn phí do thiếu FIRECRAWL_API_KEY"}
    except Exception as exc:
        return err("read_url", exc)

