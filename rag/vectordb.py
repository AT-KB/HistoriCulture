# rag/vectordb.py
from __future__ import annotations

import chromadb
from typing import List, Dict, Any

DB_PATH = "./db"
COLLECTION_NAME = "histriculture"

class VectorDB:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=DB_PATH)
        # --- ★★★★★ ここが最後の修正点 ★★★★★ ---
        # ChromaDBにデフォルトのEmbedding Functionを使わせないように、
        # embedding_function=None を明示的に指定します。
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=None # これで勝手なモデルダウンロードが止まる
        )
        # ---

    def add(self, documents: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Adds documents WITH their pre-computed embeddings."""
        if not documents: return
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} documents to ChromaDB.")

    def query(self, query_embedding: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        """Queries the collection with a pre-made vector embedding."""
        res = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        return [
            {"document": doc, "metadata": meta}
            for doc, meta in zip(docs, metas)
        ]
