from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from rag.config import (
    CHROMA_DIR,
    COLLECTION_COMPETITION_KB,
    EMBEDDING_BACKEND,
    KNOWLEDGE_DIR,
    LOCAL_EMBED_MODEL,
    OPENAI_EMBED_MODEL,
    archetype_collection,
    knowledge_paths_for_collection,
)
from rag.ingest import DocumentChunk, load_documents_from_dirs


def get_embedding_function():
    if EMBEDDING_BACKEND == "openai":
        import os

        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
        base = os.getenv("OPENAI_BASE_URL") or os.getenv("LLM_BASE_URL")
        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            api_base=base,
            model_name=OPENAI_EMBED_MODEL,
        )
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=LOCAL_EMBED_MODEL
    )


def get_client() -> chromadb.PersistentClient:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def build_collection(collection_name: str, *, reset: bool = False) -> int:
    dirs = knowledge_paths_for_collection(collection_name)
    if not dirs:
        raise FileNotFoundError(
            f"集合 {collection_name} 无对应知识目录，请先在 knowledge/ 下创建文件。"
        )

    chunks: list[DocumentChunk] = load_documents_from_dirs(dirs)
    if not chunks:
        raise ValueError(f"集合 {collection_name} 未解析到任何文本片段。")

    client = get_client()
    ef = get_embedding_function()

    if reset:
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass

    coll = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    # 分批写入
    batch = 64
    for i in range(0, len(chunks), batch):
        part = chunks[i : i + batch]
        coll.add(
            ids=[c.chunk_id for c in part],
            documents=[c.text for c in part],
            metadatas=[c.metadata for c in part],
        )

    return len(chunks)


def list_archetype_collections() -> list[str]:
    if not KNOWLEDGE_DIR.exists():
        return []
    names = []
    for p in KNOWLEDGE_DIR.iterdir():
        if p.is_dir() and p.name.startswith("archetype_"):
            names.append(p.name)
    return sorted(names)


def build_all(*, reset: bool = False) -> dict[str, int]:
    stats: dict[str, int] = {}
    stats[COLLECTION_COMPETITION_KB] = build_collection(
        COLLECTION_COMPETITION_KB, reset=reset
    )
    for folder in list_archetype_collections():
        stats[folder] = build_collection(folder, reset=reset)
    return stats
