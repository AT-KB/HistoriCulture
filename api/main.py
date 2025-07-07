# api/main.py
from __future__ import annotations

import asyncio
from typing import Dict

from fastapi import FastAPI, Request, BackgroundTasks, Form
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from scripts import search, crawl
from rag.chunk import chunk_text
from rag.vectordb import VectorDB
from rag.generate import answer
from rag.embed import GeminiEmbedding # ★ Ingestでも使うのでインポート

app = FastAPI(title="Histriculture API")
templates = Jinja2Templates(directory="templates")

class IngestRequest(BaseModel):
    query: str
    num_results: int = 10 # デフォルトの検索件数を少し増やす

def ingest_pipeline(query: str, num_results: int):
    """The complete RAG ingestion process, now using Gemini for embeddings."""
    print(f"Background ingestion started for query: '{query}'")
    
    # 1. Search & Crawl
    results = search.run(query, num_results)
    urls = [r["url"] for r in results if r.get("url")]
    if not urls:
        print(f"No URLs found for '{query}'.")
        return
    pages = asyncio.run(crawl.run(urls))

    # 2. Chunk all documents
    all_chunks = []
    for page in pages:
        all_chunks.extend(chunk.split_text(page))

    if not all_chunks:
        print("No text chunks to ingest.")
        return

    documents = [c['text'] for c in all_chunks]
    metadatas = [c['metadata'] for c in all_chunks]
    ids = [f"{m['source_url']}_{m['chunk_id']}" for m in metadatas]

    # 3. ★★★★★ ここが最重要の修正点 ★★★★★
    # GeminiのEmbedderを呼び出し、全ドキュメントをベクトル化する
    print(f"Embedding {len(documents)} chunks with Gemini...")
    embedder = GeminiEmbedding()
    embeddings = embedder.embed_documents(documents)
    print("Embedding complete.")

    # 4. Store documents AND their embeddings in the DB
    db = VectorDB()
    db.add(documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids)
    
    print(f"Background ingestion finished for query: '{query}'.")

# (他のエンドポイントは変更なし)
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.post("/ingest")
async def ingest(req: IngestRequest, background_tasks: BackgroundTasks) -> Dict[str, str]:
    background_tasks.add_task(ingest_pipeline, req.query, req.num_results)
    return {"message": f"Ingestion process for '{req.query}' has been started."}

@app.post("/ask")
async def ask(question: str = Form(...)):
    db = VectorDB()
    response_generator = answer(question, db)
    return StreamingResponse(response_generator, media_type="text/plain")
