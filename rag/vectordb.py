from __future__ import annotations

import logging
from typing import List, Dict, Any

import chromadb
from rag.embed import embed_texts, embedder

logger = logging.getLogger(__name__)

DB_PATH = "/app/db"  # Volume マウントに合わせる
COLLECTION_NAME = "histriculture"


class VectorDB:
    def __init__(self) -> None:
        try:
            self.client = chromadb.PersistentClient(path=DB_PATH)
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=embedder.embed_query,  # 埋め込み関数
            )
        except Exception as e:
            logger.error(f"ChromaDB init error: {e}")
            raise

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
