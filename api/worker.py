# api/worker.py
"""
Scheduled ingestion worker.
This script is intended to be run by a cron job to periodically trigger
the data ingestion process for a set of predefined topics.
"""
from __future__ import annotations

import os
from typing import List

import requests

# The base URL of the running API service.
# In Railway, this should be set to the service's public URL.
API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

# Default topics to re-ingest periodically.
DEFAULT_TOPICS: List[str] = [
    "インドの歴史",
    "ムガル帝国",
    "インダス文明",
    "ガンディーの生涯",
    "アショーカ王",
]

def trigger_ingestion(topic: str) -> None:
    """Sends a POST request to the ingestion endpoint for a single topic."""
    ingest_url = f"{API_BASE_URL}/ingest"
    print(f"Triggering ingestion for topic: '{topic}' -> {ingest_url}")
    
    try:
        # The /ingest endpoint expects a JSON body like {"query": "...", "num_results": ...}
        # We can use the default num_results from the API.
        response = requests.post(
            ingest_url,
            json={"query": topic},
            timeout=15  # Set a timeout for the request
        )
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        print(f"Successfully triggered ingestion for: '{topic}'. Response: {response.json()}")
    except requests.RequestException as e:
        print(f"ERROR: Failed to trigger ingestion for '{topic}'. Reason: {e}")

def main() -> None:
    """Triggers the ingestion process for all predefined topics."""
    print("--- Starting nightly re-ingestion worker ---")
    for topic in DEFAULT_TOPICS:
        trigger_ingestion(topic)
    print("--- Finished nightly re-ingestion worker ---")


if __name__ == "__main__":
    main()
