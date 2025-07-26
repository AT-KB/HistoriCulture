# rag/embed.py
from __future__ import annotations

import os
from typing import List

import google.generativeai as genai

# Configure genai once when the module is loaded
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Use the latest and recommended embedding model
EMBEDDING_MODEL = "models/text-embedding-004"

class GeminiEmbedding:
    """A dedicated class to handle Gemini embeddings."""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of documents for storage."""
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=texts,
            task_type="RETRIEVAL_DOCUMENT"
        )
        return result["embedding"]

    def embed_query(self, text: str) -> List[float]:
        """Embeds a single query for retrieval."""
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="RETRIEVAL_QUERY"
        )
        return result["embedding"]


embedder = GeminiEmbedding()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Convenience wrapper to embed multiple texts."""
    return embedder.embed_documents(texts)
