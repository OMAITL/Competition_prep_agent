from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

SUPPORTED_SUFFIXES = {".md", ".txt", ".markdown"}


@dataclass
class DocumentChunk:
    text: str
    source: str
    chunk_id: str
    metadata: dict


def _split_paragraphs(text: str) -> list[str]:
    parts = re.split(r"\n\s*\n+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def chunk_text(
    text: str,
    source: str,
    *,
    chunk_size: int = 500,
    overlap: int = 80,
) -> list[DocumentChunk]:
    """按字符窗口切片，保留段落边界优先。"""
    paragraphs = _split_paragraphs(text)
    if not paragraphs:
        return []

    chunks: list[DocumentChunk] = []
    buffer = ""
    idx = 0

    def flush(buf: str) -> None:
        nonlocal idx
        if not buf.strip():
            return
        chunks.append(
            DocumentChunk(
                text=buf.strip(),
                source=source,
                chunk_id=f"{source}#{idx}",
                metadata={"source": source, "chunk_index": idx},
            )
        )
        idx += 1

    for para in paragraphs:
        if len(buffer) + len(para) + 2 <= chunk_size:
            buffer = f"{buffer}\n\n{para}".strip() if buffer else para
        else:
            if buffer:
                flush(buffer)
                if overlap and len(buffer) > overlap:
                    buffer = buffer[-overlap:] + "\n\n" + para
                else:
                    buffer = para
            else:
                # 单段超长：硬切
                start = 0
                while start < len(para):
                    piece = para[start : start + chunk_size]
                    flush(piece)
                    start += chunk_size - overlap
                buffer = ""

    if buffer:
        flush(buffer)

    return chunks


def load_documents_from_dirs(dirs: list[Path]) -> list[DocumentChunk]:
    all_chunks: list[DocumentChunk] = []
    for base in dirs:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = path.read_text(encoding="gbk", errors="ignore")
            try:
                from rag.config import KNOWLEDGE_DIR

                rel = str(path.relative_to(KNOWLEDGE_DIR))
            except ValueError:
                rel = str(path)
            all_chunks.extend(chunk_text(text, source=rel))
    return all_chunks
