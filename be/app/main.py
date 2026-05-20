from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import rag

app = FastAPI(title="Welfare RAG API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int | None = None


class Source(BaseModel):
    service_name: str
    source: str
    source_url: str
    distance: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    answer_text, docs = rag.answer(req.query, top_k=req.top_k)
    sources = [
        Source(
            service_name=d.metadata.get("service_name", ""),
            source=d.metadata.get("source", ""),
            source_url=d.metadata.get("source_url", ""),
            distance=d.distance,
        )
        for d in docs
    ]
    return ChatResponse(answer=answer_text, sources=sources)
