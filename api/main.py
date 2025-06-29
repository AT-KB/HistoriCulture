from __future__ import annotations

import asyncio
from typing import List

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from scripts import search, crawl
from rag.chunk import chunk_text
from rag.vectordb import VectorDB
from rag.generate import answer

app = FastAPI()
templates = Jinja2Templates(directory="templates")
DB = VectorDB()


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


class IngestRequest(BaseModel):
    query: str
    num_results: int = 3


class AskRequest(BaseModel):
    question: str


@app.post("/ingest")
async def ingest(req: IngestRequest) -> dict:
    results = search.run(req.query, req.num_results)
    urls = [r["url"] for r in results]
    texts = await crawl.run(urls)
    for url, text in texts.items():
        for idx, chunk in enumerate(chunk_text(text)):
            DB.add([chunk], [{"url": url}], [f"{url}_{idx}"])
    return {"ingested": len(texts)}


@app.post("/ask")
async def ask(req: AskRequest):
    async def generate():
        for piece in answer(req.question, DB):
            yield piece
            await asyncio.sleep(0)

    return StreamingResponse(generate(), media_type="text/plain")
