from __future__ import annotations

import logging
from typing import List, Dict, Any

import chromadb
from rag.embed import embed_texts, embedder

logger = logging.getLogger(__name__)

DB_PATH = "/app/db"
COLLECTION_NAME = "histriculture"


class VectorDB:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path=DB_PATH)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedder.embed_query,
        )

    def add(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> None:
        if not documents:
            return
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )
        logger.info(f"Added {len(documents)} documents to ChromaDB.")

    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        embedding = embed_texts([query_text])[0]
        res = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
        )
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        return [{"document": d, "metadata": m} for d, m in zip(docs, metas)]
