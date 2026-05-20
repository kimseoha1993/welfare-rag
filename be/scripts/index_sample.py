"""샘플 복지 데이터를 청킹·임베딩하여 Chroma에 적재."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app import config
from app.rag import get_vectorstore

SAMPLE_PATH = ROOT / "data" / "sample_welfare.json"


def build_documents(records: list[dict]) -> list[Document]:
    docs: list[Document] = []
    for r in records:
        body = (
            f"[서비스명] {r['service_name']}\n"
            f"[대상] {r['target']}\n"
            f"[내용] {r['content']}\n"
            f"[신청방법] {r['how_to_apply']}"
        )
        docs.append(
            Document(
                page_content=body,
                metadata={
                    "id": r["id"],
                    "service_name": r["service_name"],
                    "category": r["category"],
                    "source": r["source"],
                    "source_url": r["source_url"],
                    "status": "official",
                },
            )
        )
    return docs


def main() -> None:
    records = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    print(f"[load] {len(records)}건")

    base_docs = build_documents(records)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    chunks = splitter.split_documents(base_docs)
    print(f"[chunk] {len(chunks)}개 청크")

    vs = get_vectorstore()
    # 컬렉션이 이미 있으면 비우고 다시 적재 (개발 단계용)
    try:
        existing = vs.get()
        if existing and existing.get("ids"):
            vs.delete(ids=existing["ids"])
            print(f"[reset] 기존 {len(existing['ids'])}개 제거")
    except Exception as e:
        print(f"[reset] skip: {e}")

    ids = [f"{c.metadata['id']}_{i}" for i, c in enumerate(chunks)]
    vs.add_documents(documents=chunks, ids=ids)
    print(f"[done] {len(ids)}개 인덱싱 완료 → {config.CHROMA_PATH}")


if __name__ == "__main__":
    main()
