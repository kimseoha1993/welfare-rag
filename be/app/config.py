import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:3b")

_chroma = os.getenv("CHROMA_PATH", "./chroma_db")
CHROMA_PATH = str(
    Path(_chroma) if Path(_chroma).is_absolute() else BASE_DIR / _chroma
)

COLLECTION_NAME = os.getenv("COLLECTION_NAME", "welfare")
TOP_K = int(os.getenv("TOP_K", "4"))
DISTANCE_THRESHOLD = float(os.getenv("DISTANCE_THRESHOLD", "0.6"))
