from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup
from readability import Document


SEMAPHORE: asyncio.Semaphore = asyncio.Semaphore(3)


async def _fetch(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    async with SEMAPHORE:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                resp.raise_for_status()
                html = await resp.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            print(f"Warning: failed to fetch {url}: {exc}")
            return None
    doc = Document(html)
    content = doc.summary()
    text = BeautifulSoup(content, "lxml").get_text(separator="\n")
    return text


async def run(urls: List[str]) -> Dict[str, str]:
    """Fetch multiple URLs concurrently and return cleaned text."""
    async with aiohttp.ClientSession() as session:
        tasks = [_fetch(session, url) for url in urls]
        texts = await asyncio.gather(*tasks, return_exceptions=True)
    results = {}
    for url, text in zip(urls, texts):
        if text is None or isinstance(text, Exception):
            continue
        results[url] = text
    return results
