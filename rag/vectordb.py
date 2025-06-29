from __future__ import annotations

import os
from typing import Any, Dict, List

import chromadb
from chromadb.utils import embedding_functions

from .embed import embed_texts


class GeminiEmbeddingFunction(embedding_functions.DefaultEmbeddingFunction):
    def __call__(self, texts: List[str]) -> List[List[float]]:
        return embed_texts(texts)


class VectorDB:
    def __init__(self, path: str = "db") -> None:
        self.client = chromadb.PersistentClient(path)
        self.collection = self.client.get_or_create_collection(
            "docs", embedding_function=GeminiEmbeddingFunction()
        )

    def add(self, docs: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        self.collection.add(documents=docs, metadatas=metadatas, ids=ids)

    def query(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        res = self.collection.query(query_texts=[query], n_results=n_results)
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        return [
            {"document": doc, "metadata": meta}
            for doc, meta in zip(docs, metas)
        ]
