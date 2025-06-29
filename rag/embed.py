from __future__ import annotations

import os
from typing import List

import google.generativeai as genai


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a list of texts using Gemini embeddings."""
    embeddings = []
    for text in texts:
        result = genai.embed_content(model="models/embedding-001", content=text)
        embeddings.append(result["embedding"])  # type: ignore[index]
    return embeddings
