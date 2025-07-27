# api/main.py

from __future__ import annotations
import logging
from typing import Dict

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ValidationError  # ValidationError追加

from scripts import search, crawl
from rag.chunk import chunk_text
from rag.embed import embed_texts
from rag.vectordb import VectorDB
from rag.generate import answer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="HistoriCulture API")
templates = Jinja2Templates(directory="templates")
DB = VectorDB()


class IngestRequest(BaseModel):
    query: str
    num_results: int = 10


class AskRequest(BaseModel):
    query: str  # question → queryに変更（HTML/一貫性）


async def ingest_pipeline(query: str, num_results: int = 10) -> int:  # default=10に調整
    """Run the ingestion pipeline (search → crawl → chunk → embed → DB.add) and return ingested chunk count."""
    try:
        results = search.run(query, num_results)
        urls = [r["url"] for r in results if r.get("url")]
        logger.info(f"[DEBUG] URLs for '{query}': {urls}")
        if not urls:
            logger.info(f"No URLs for query '{query}'")
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
    except Exception as e:
        logger.error(f"Ingestion pipeline error: {e}")
        raise


@app.get("/status")
async def status() -> Dict[str, int]:
    """Return the number of stored chunks in the vector database."""
    count = DB.collection.count()
    return {"stored_chunks": count}


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest")
async def ingest(req: IngestRequest) -> Dict[str, int]:
    try:
        count = await ingest_pipeline(req.query, req.num_results)
        return {"ingested": count}
    except Exception:
        logger.exception("Ingestion pipeline failed")
        raise HTTPException(status_code=500, detail="Ingestion error")


@app.post("/ask")
async def ask(req: AskRequest):
    """
    Accepts JSON {"query": "..."} and returns a streaming RAG answer.
    """
    try:
        question = req.query  # req.question → req.query
        response_generator = answer(question, DB)
        return StreamingResponse(response_generator, media_type="text/plain")
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Ask error")
        raise HTTPException(status_code=500, detail=str(e))
