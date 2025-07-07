# api/worker.py
from __future__ import annotations

from api.main import ingest_pipeline

DEFAULT_TOPICS = [
    "インドの歴史",
    "ムガル帝国",
    "ガンディーの生涯",
]

def main() -> None:
    print("--- Starting direct ingestion worker ---")
    for topic in DEFAULT_TOPICS:
        try:
            ingest_pipeline(query=topic, num_results=10)
        except Exception as e:
            print(f"ERROR during ingestion for '{topic}': {e}")
    print("--- Finished direct ingestion worker ---")

if __name__ == "__main__":
    main()
