from __future__ import annotations

from rag.config import COLLECTION_COMPETITION_KB, RAG_TOP_K, archetype_collection
from rag.index import get_client, get_embedding_function


def retrieve(
    query: str,
    collection_name: str,
    *,
    top_k: int | None = None,
) -> list[dict]:
    """返回 [{text, source, distance}, ...]"""
    k = top_k or RAG_TOP_K
    client = get_client()
    ef = get_embedding_function()
    try:
        coll = client.get_collection(
            name=collection_name, embedding_function=ef
        )
    except Exception:
        return []

    if not query.strip():
        return []

    res = coll.query(query_texts=[query], n_results=k)
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]

    out: list[dict] = []
    for doc, meta, dist in zip(docs, metas, dists):
        out.append(
            {
                "text": doc,
                "source": (meta or {}).get("source", "unknown"),
                "distance": dist,
            }
        )
    return out


def retrieve_for_competition(
    competition_name: str,
    archetype: str,
    *,
    extra_query: str = "",
    top_k: int | None = None,
) -> dict[str, list[dict]]:
    """Prompt1 用：通用库 + 赛道库。"""
    q_base = f"{competition_name} {archetype} {extra_query}".strip()
    return {
        "competition_kb": retrieve(
            f"{q_base} 赛制 规则 提交 评分",
            COLLECTION_COMPETITION_KB,
            top_k=top_k,
        ),
        "archetype": retrieve(
            f"{q_base} 备赛 学习路径 教程 入门",
            archetype_collection(archetype),
            top_k=top_k,
        ),
    }


def format_rag_context(chunks: list[dict], *, max_chars: int = 6000) -> str:
    if not chunks:
        return "（知识库未命中或未建索引）"

    lines: list[str] = []
    total = 0
    for i, c in enumerate(chunks, 1):
        block = f"[{i}] (source: {c.get('source', '?')})\n{c.get('text', '')}\n"
        if total + len(block) > max_chars:
            break
        lines.append(block)
        total += len(block)
    return "\n".join(lines)


def merge_retrieval_results(results: dict[str, list[dict]]) -> list[dict]:
    seen: set[str] = set()
    merged: list[dict] = []
    for key in ("competition_kb", "archetype"):
        for item in results.get(key, []):
            sig = item.get("text", "")[:120]
            if sig in seen:
                continue
            seen.add(sig)
            merged.append(item)
    return merged
