from __future__ import annotations

import asyncio
import os
from typing import Any

import pandas as pd
import httpx


async def ingest_one(client: httpx.AsyncClient, name: str) -> None:
    try:
        resp = await client.post("/ingest?num_results=5", json={"query": name})
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()
        count = data.get("ingested", 0)
        print(f"[OK ] {name} \u2192 ingested {count}")
    except Exception as exc:
        print(f"[NG ] {name} \u2192 {exc}")


async def main() -> None:
    df = pd.read_excel("data_j.xls", sheet_name="Sheet1", dtype=str)
    cols = ["コード", "銘柄名", "市場・商品区分", "33業種区分"]
    df = df[cols]
    df = df.dropna(how="all")

    api_url = os.getenv("API_URL", "http://localhost:8000")
    async with httpx.AsyncClient(base_url=api_url) as client:
        for name in df["銘柄名"].dropna():
            await ingest_one(client, name)


if __name__ == "__main__":
    asyncio.run(main())
