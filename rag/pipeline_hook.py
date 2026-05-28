"""供主 Agent 流水线调用的 RAG 封装。"""
from __future__ import annotations

from rag.retrieve import (
    format_rag_context,
    merge_retrieval_results,
    retrieve_for_competition,
    retrieve_for_prep_plan,
    retrieve_for_resources,
)


def build_rag_context_for_prompt1(
    competition_name: str,
    archetype: str,
    *,
    track: str = "",
    top_k: int | None = None,
) -> str:
    extra = track or ""
    raw = retrieve_for_competition(
        competition_name, archetype, extra_query=extra, top_k=top_k
    )
    return format_rag_context(merge_retrieval_results(raw))


def build_rag_context_for_prompt2(
    competition_name: str,
    archetype: str,
    *,
    goal: str = "",
    top_k: int | None = None,
) -> str:
    """检索点 A′：路径规划前，优先 competition_kb / override。"""
    raw = retrieve_for_prep_plan(
        competition_name, archetype, extra_query=goal, top_k=top_k
    )
    return format_rag_context(merge_retrieval_results(raw))


def build_rag_context_for_prompt3(
    competition_name: str,
    archetype: str,
    *,
    focus: str = "资料 教程 工具 开源",
    top_k: int | None = None,
) -> str:
    raw = retrieve_for_resources(
        competition_name,
        archetype,
        extra_query=focus,
        top_k=top_k,
    )
    return format_rag_context(merge_retrieval_results(raw))
