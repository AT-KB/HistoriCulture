from __future__ import annotations

import os
from typing import List, Dict

from googleapiclient.discovery import build


SERVICE = build("customsearch", "v1", developerKey=os.getenv("CSE_KEY"))


def run(query: str, num: int = 10) -> List[Dict[str, str]]:
    """Run Google Custom Search and return list of results.

    Args:
        query: Search query string.
        num: Number of search results to return.

    Returns:
        List of dicts containing URL and title sorted by rank.
    """
    res = SERVICE.cse().list(q=query, cx=os.getenv("CSE_CX"), num=num).execute()
    items = res.get("items", [])
    results = [{"url": item.get("link"), "title": item.get("title")} for item in items]
    return results
