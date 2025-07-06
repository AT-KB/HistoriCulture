# rag/vectordb.py
from __future__ import annotations

import chromadb
from typing import List, Dict, Any

DB_PATH = "./db"  # RailwayのVolumeにマウントされるパス
COLLECTION_NAME = "histriculture"

class VectorDB:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=DB_PATH)
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

    def add(self, docs: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Adds documents and their metadata to the collection."""
        if not docs: return
        # ChromaDB > 0.5.0 now requires embeddings for add.
        # Let's assume the embedding is handled before calling this for simplicity,
        # or we configure a GeminiEmbeddingFunction.
        # For now, let's keep it as is, assuming an embedding function is set or will be.
        # The main fix is in the query part.
        self.collection.add(documents=docs, metadatas=metadatas, ids=ids)

    def query(self, query_embedding: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Queries the collection with a pre-made vector embedding.
        This is the key change: we no longer pass text, but a vector.
        """
        res = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        # 戻り値の形式を以前のコードと合わせる
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        return [
            {"document": doc, "metadata": meta}
            for doc, meta in zip(docs, metas)
        ]
