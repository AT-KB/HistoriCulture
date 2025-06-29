from __future__ import annotations

import asyncio
import os

import httpx

DEFAULT_TOPICS = ["history", "culture"]


async def ingest_topic(client: httpx.AsyncClient, topic: str) -> None:
    await client.post("/ingest", json={"query": topic})


async def main() -> None:
    api_url = os.getenv("API_URL", "http://localhost:8000")
    async with httpx.AsyncClient(base_url=api_url) as client:
        for topic in DEFAULT_TOPICS:
            await ingest_topic(client, topic)


if __name__ == "__main__":
    asyncio.run(main())
