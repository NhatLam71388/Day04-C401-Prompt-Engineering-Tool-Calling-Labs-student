from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err


import urllib.request
import urllib.parse
import json

def web_search(query: str = "", topic: str = "general", timeframe: str | None = "week", max_results: int = 5) -> dict[str, Any]:
    try:
        # Check if Tavily key exists, otherwise fallback to FREE Wikipedia API
        key = os.getenv("TAVILY_API_KEY")
        if key:
            body: dict[str, Any] = {"query": query, "topic": topic, "max_results": int(max_results or 5), "search_depth": "basic"}
            if timeframe:
                body["time_range"] = timeframe
            response = requests.post(
                "https://api.tavily.com/search",
                json=body,
                headers={"Authorization": f"Bearer {key}"},
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            items = [{
                "title": item.get("title"),
                "url": item.get("url"),
                "source": domain(item.get("url", "")),
                "summary": item.get("content"),
                "score": item.get("score"),
            } for item in data.get("results", [])]
            return {"tool": "web_search", "query": query, "topic": topic, "timeframe": timeframe, "items": items}
        
        # FREE FALLBACK: Wikipedia API
        url = "https://vi.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query",
            "list": "search",
            "srsearch": query,
            "utf8": "",
            "format": "json",
            "srlimit": max_results
        })
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        data = json.loads(html)
        
        items = []
        for item in data.get("query", {}).get("search", []):
            items.append({
                "title": item.get("title"),
                "url": f"https://vi.wikipedia.org/wiki/{urllib.parse.quote(item.get('title'))}",
                "source": "vi.wikipedia.org",
                "summary": item.get("snippet", "").replace('<span class="searchmatch">', '').replace('</span>', ''),
                "score": 1.0,
            })
            
        if not items:
            items = [{"title": "Không tìm thấy kết quả", "url": "", "source": "", "summary": f"Không tìm thấy dữ liệu trên Wikipedia cho '{query}'"}]
            
        return {"tool": "web_search", "query": query, "topic": topic, "timeframe": timeframe, "items": items, "note": "Sử dụng API miễn phí (Wikipedia) do thiếu TAVILY_API_KEY"}
    except Exception as exc:
        return err("web_search", exc)

