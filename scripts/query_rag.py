#!/usr/bin/env python3
"""命令行试检索 RAG。"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rag.config import COLLECTION_COMPETITION_KB
from rag.retrieve import format_rag_context, retrieve, retrieve_for_competition


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--collection", default=COLLECTION_COMPETITION_KB)
    parser.add_argument("--archetype", default="", help="若提供则同时查 competition_kb + archetype")
    parser.add_argument("--name", default="", help="比赛名称，配合 --archetype")
    parser.add_argument("-k", type=int, default=5)
    args = parser.parse_args()

    if args.archetype and args.name:
        res = retrieve_for_competition(args.name, args.archetype, top_k=args.k)
        from rag.retrieve import merge_retrieval_results

        merged = merge_retrieval_results(res)
        print(format_rag_context(merged))
        return

    hits = retrieve(args.query, args.collection, top_k=args.k)
    for i, h in enumerate(hits, 1):
        print(f"--- [{i}] dist={h.get('distance')} source={h.get('source')}")
        print(h.get("text", "")[:500])
        print()


if __name__ == "__main__":
    main()
