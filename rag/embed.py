from __future__ import annotations
import os
from typing import List
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
EMBEDDING_MODEL = "models/text-embedding-004"

class GeminiEmbedding:
    """Gemini で文書／クエリを埋め込む"""

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """複数文書を順番に埋め込む（戻り値は 2-D List）"""
        embeddings: List[List[float]] = []
        for t in texts:
            res = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=t,
                task_type="RETRIEVAL_DOCUMENT",
            )
            embeddings.append(res["embedding"])
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        res = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type="RETRIEVAL_QUERY",
        )
        return res["embedding"]

embedder = GeminiEmbedding()

def embed_texts(texts: List[str]) -> List[List[float]]:
    return embedder.embed_documents(texts)
