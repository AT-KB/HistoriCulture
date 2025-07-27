from __future__ import annotations
import chromadb
from typing import List, Dict, Any
from rag.embed import embed_texts, embedder  # embedder追加

DB_PATH = "/app/db"  # Volumeマウントに合わせ
COLLECTION_NAME = "histriculture"

class VectorDB:
    def __init__(self) -> None:
        try:
            self.client = chromadb.PersistentClient(path=DB_PATH)
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=embedder.embed_query  # 埋め込み関数指定
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
        print(f"Added {len(documents)} documents to ChromaDB.")

    def query(
        self,
        query_text: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        # テキスト→埋め込み
        embedding = embed_texts([query_text])[0]
        # ベクトル検索
        res = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results
        )
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        return [
            {"document": d, "metadata": m}
            for d, m in zip(docs, metas)
        ]
