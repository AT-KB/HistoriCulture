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

app = FastAPI(title="Histriculture API")
templates = Jinja2Templates(directory="templates")

# --- Pydantic Models (for Ingest only) ---
class IngestRequest(BaseModel):
    query: str
    num_results: int = 3

# --- Helper function for background ingestion ---
def ingest_pipeline(query: str, num_results: int):
    print(f"Background ingestion started for query: '{query}'")
    results = search.run(query, num_results)
    urls = [r["url"] for r in results]
    if not urls:
        print(f"No URLs found for '{query}'.")
        return
    texts = asyncio.run(crawl.run(urls))
    db = VectorDB()
    for url, text in texts.items():
        chunks = chunk_text(text)
        if not chunks: continue
        ids = [f"{url}_{idx}" for idx, _ in enumerate(chunks)]
        metadatas = [{"url": url} for _ in chunks]
        db.add(chunks, metadatas, ids)
    print(f"Background ingestion finished for query: '{query}'.")

# --- API Endpoints ---

@app.get("/")
async def index(request: Request):
    """Serves the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/ingest")
async def ingest(req: IngestRequest, background_tasks: BackgroundTasks) -> Dict[str, str]:
    """Triggers background ingestion."""
    background_tasks.add_task(ingest_pipeline, req.query, req.num_results)
    return {"message": f"Ingestion process for '{req.query}' has been started."}

@app.post("/ask")
async def ask(question: str = Form(...)):
    """
    Receives a question from the HTMX form, streams the RAG response.
    """
    db = VectorDB()
    
    # The async generator from rag/generate.py
    response_generator = answer(question, db)

    # Return the generator as a streaming response for HTMX
    return StreamingResponse(response_generator, media_type="text/plain")
