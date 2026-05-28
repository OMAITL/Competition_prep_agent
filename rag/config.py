from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = ROOT / "knowledge"
CHROMA_DIR = ROOT / "data" / "chroma"

RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "local").lower()

# 本地多语言模型，适合中文备赛文档
LOCAL_EMBED_MODEL = os.getenv(
    "LOCAL_EMBED_MODEL", "paraphrase-multilingual-MiniLM-L12-v2"
)
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

COLLECTION_COMPETITION_KB = "competition_kb"


def archetype_collection(archetype: str) -> str:
    safe = archetype.strip().lower().replace(" ", "_")
    return f"archetype_{safe}"


def knowledge_paths_for_collection(collection: str) -> list[Path]:
    """返回某集合应索引的目录列表。"""
    paths: list[Path] = []
    if collection == COLLECTION_COMPETITION_KB:
        shared = KNOWLEDGE_DIR / "shared"
        overrides = KNOWLEDGE_DIR / "overrides"
        if shared.exists():
            paths.append(shared)
        if overrides.exists():
            paths.append(overrides)
    elif collection.startswith("archetype_"):
        arch = collection.removeprefix("archetype_")
        p = KNOWLEDGE_DIR / f"archetype_{arch}"
        if p.exists():
            paths.append(p)
    return paths
