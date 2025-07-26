# api/worker.py
from __future__ import annotations

import asyncio
from api.main import ingest_pipeline

DEFAULT_TOPICS = [
    "インドの歴史",
    "ムガル帝国",
    "ガンディーの生涯",
]


def main() -> None:
    print("--- Starting direct ingestion worker ---")
    total = 0
    for topic in DEFAULT_TOPICS:
        try:
            count = asyncio.run(ingest_pipeline(topic, num_results=10))
            total += count
            print(f"[OK ] {topic} → ingested {count} chunks")
        except Exception as e:
            print(f"[NG ] {topic} → {e}")
    print(f"--- Finished ingestion: total {total} chunks ---")


if __name__ == "__main__":
    main()
