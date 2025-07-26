# api/main.py
from __future__ import annotations

import asyncio
from typing import Dict

from fastapi import FastAPI, Request, Form, HTTPException
import logging
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from scripts import search, crawl
from rag.chunk import chunk_text
from rag.vectordb import VectorDB
from rag.generate import answer
from rag.embed import GeminiEmbedding

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB = VectorDB()

app = FastAPI(title="Histriculture API")
templates = Jinja2Templates(directory="templates")


class IngestRequest(BaseModel):
    query: str
    num_results: int = 10


async def ingest_pipeline(query: str, num_results: int = 3) -> int:
    """Run the ingestion pipeline and return number of chunks added."""
    results = search.run(query, num_results)
    urls = [r["url"] for r in results]
    texts = await crawl.run(urls)
    count = 0
    for url, text in texts.items():
        for idx, chunk in enumerate(chunk_text(text)):
            try:
                DB.add([chunk], [{"url": url}], [f"{url}_{idx}"])
                count += 1
            except Exception as e:
                logger.error(f"Failed to add chunk for {url}: {e}")
    return count


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
    except Exception as e:
        logger.exception("Ingestion failed")
        raise HTTPException(status_code=500, detail="Ingestion error") from e


@app.post("/ask")
async def ask(question: str = Form(...)):
    db = VectorDB()
    response_generator = answer(question, db)
    return StreamingResponse(response_generator, media_type="text/plain")
