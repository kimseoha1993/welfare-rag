from __future__ import annotations

from dataclasses import dataclass

from langchain_chroma import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings

from . import config

SYSTEM_PROMPT = "당신은 한국 복지 서비스 안내 어시스턴트입니다. 참고 문서에만 근거해 한국어로 정확하게 답하세요."

ANSWER_TEMPLATE = """다음 참고 문서를 바탕으로 질문에 답하세요.
문서에 없는 내용은 추측하지 말고 "해당 정보는 데이터에 없습니다"라고 답하세요.

[참고 문서]
{context}

[질문]
{query}

[답변]
"""


@dataclass
class RetrievedDoc:
    content: str
    metadata: dict
    distance: float


_embeddings = None
_vectorstore = None
_llm = None


def get_embeddings() -> OllamaEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = OllamaEmbeddings(
            model=config.EMBED_MODEL,
            base_url=config.OLLAMA_BASE_URL,
        )
    return _embeddings


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            collection_name=config.COLLECTION_NAME,
            embedding_function=get_embeddings(),
            persist_directory=config.CHROMA_PATH,
            collection_metadata={"hnsw:space": "cosine"},
        )
    return _vectorstore


def get_llm() -> ChatOllama:
    global _llm
    if _llm is None:
        _llm = ChatOllama(
            model=config.LLM_MODEL,
            base_url=config.OLLAMA_BASE_URL,
            temperature=0.2,
        )
    return _llm


def retrieve(query: str, top_k: int | None = None) -> list[RetrievedDoc]:
    k = top_k or config.TOP_K
    results = get_vectorstore().similarity_search_with_score(query, k=k)
    docs: list[RetrievedDoc] = []
    for doc, distance in results:
        if distance < config.DISTANCE_THRESHOLD:
            docs.append(
                RetrievedDoc(
                    content=doc.page_content,
                    metadata=doc.metadata,
                    distance=float(distance),
                )
            )
    return docs


def generate(query: str, docs: list[RetrievedDoc]) -> str:
    if not docs:
        return "해당 정보는 데이터에 없습니다."

    context = "\n\n".join(
        f"- ({d.metadata.get('service_name', '')}) {d.content}" for d in docs
    )
    prompt = ANSWER_TEMPLATE.format(context=context, query=query)

    response = get_llm().invoke([("system", SYSTEM_PROMPT), ("user", prompt)])
    return response.content.strip()


def answer(query: str, top_k: int | None = None) -> tuple[str, list[RetrievedDoc]]:
    docs = retrieve(query, top_k=top_k)
    return generate(query, docs), docs
