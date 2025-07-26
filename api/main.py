# api/main.py
from __future__ import annotations

import logging
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from scripts import search, crawl
from rag.chunk import chunk_text
from rag.embed import embed_texts
from rag.vectordb import VectorDB
from rag.generate import answer
from fastapi import FastAPI

@app.get("/status")
async def status():
    from rag.vectordb import VectorDB
    db = VectorDB()
    count = db.collection.count()  # ChromaDB に保存されているチャンク数
    return {"stored_chunks": count}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB = VectorDB()

app = FastAPI(title="Histriculture API")
templates = Jinja2Templates(directory="templates")


class IngestRequest(BaseModel):
    query: str
    num_results: int = 10


async def ingest_pipeline(query: str, num_results: int = 3) -> int:
    """Run ingestion pipeline with debug logging and return chunk count."""
    results = search.run(query, num_results)
    urls = [r["url"] for r in results if r.get("url")]
    logger.info(f"[DEBUG] URLs for '{query}': {urls}")
    if not urls:
        return 0

    texts = await crawl.run(urls)
    total = 0

    for url, text in texts.items():
        chunks = chunk_text(text)
        logger.info(f"[DEBUG] '{url}' produced {len(chunks)} chunks")
        embeddings = embed_texts(chunks)
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            try:
                DB.add(
                    documents=[chunk],
                    embeddings=[embedding],
                    metadatas=[{"url": url}],
                    ids=[f"{url}_{idx}"]
                )
                total += 1
            except Exception as e:
                logger.error(f"Failed to add chunk for {url}: {e}")

    logger.info(f"Ingested total {total} chunks for '{query}'")
    return total


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/ingest")
async def ingest(req: IngestRequest) -> dict:
    try:
        count = await ingest_pipeline(req.query, req.num_results)
        return {"ingested": count}
    except Exception:
        logger.exception("Ingestion pipeline failed")
        raise HTTPException(status_code=500, detail="Ingestion error")


@app.post("/ask")
async def ask(question: str = Form(...)):
    db = VectorDB()
    response_generator = answer(question, db)
    return StreamingResponse(response_generator, media_type="text/plain")
