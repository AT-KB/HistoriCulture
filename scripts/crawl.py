from __future__ import annotations

import asyncio
from typing import Dict, List

import aiohttp
from bs4 import BeautifulSoup
from readability import Document


async def _fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as resp:
        html = await resp.text()
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
        if isinstance(text, Exception):
            continue
        results[url] = text
    return results
