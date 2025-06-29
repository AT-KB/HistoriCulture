"""Scheduled ingestion worker."""

import os
import requests

API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

DEFAULT_TOPICS = [
    "インドの歴史",
    "ムガル帝国",
    "インダス文明",
    "ガンディーの生涯",
]


def trigger_ingestion(topic: str) -> None:
    """Send a POST request to the ingestion endpoint for a topic."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/ingest", json={"query": topic}
        )
        response.raise_for_status()
        print(f"Successfully ingested: {topic}")
    except requests.RequestException as exc:
        print(f"Failed to ingest {topic}: {exc}")


def main() -> None:
    """Trigger ingestion for all default topics."""
    for topic in DEFAULT_TOPICS:
        trigger_ingestion(topic)


if __name__ == "__main__":
    main()
