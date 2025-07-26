from __future__ import annotations
import chromadb
from typing import List, Dict, Any
from rag.embed import embed_texts

DB_PATH = "./db"
COLLECTION_NAME = "histriculture"

class VectorDB:
    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path=DB_PATH)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=None  # 外部で埋め込みを制御する
        )

    def add(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ) -> None:
        """Adds documents with their pre-computed embeddings to ChromaDB."""
        if not documents:
            return
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )
        print(f"Added {len(documents)} documents to ChromaDB.")

    def query(
        self,
        query_text: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Accepts a raw text query, computes its embedding,
        and returns the top-n matching documents.
        """
        # テキスト → 埋め込み
        embedding = embed_texts([query_text])[0]
        # ベクトル検索
        res = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results
        )
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        return [
            {"document": doc, "metadata": meta}
            for doc, meta in zip(docs, metas)
        ]
