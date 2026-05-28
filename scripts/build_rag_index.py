#!/usr/bin/env python3
"""构建 / 重建 Chroma 向量索引。"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rag.config import COLLECTION_COMPETITION_KB
from rag.index import build_all, build_collection, list_archetype_collections


def main() -> None:
    parser = argparse.ArgumentParser(description="Build RAG vector indexes")
    parser.add_argument(
        "--collection",
        help=f"集合名，如 {COLLECTION_COMPETITION_KB} 或 archetype_math_modeling",
    )
    parser.add_argument("--all", action="store_true", help="构建 competition_kb + 所有 archetype_*")
    parser.add_argument("--reset", action="store_true", help="删除后重建")
    args = parser.parse_args()

    if args.all:
        stats = build_all(reset=args.reset)
        for name, n in stats.items():
            print(f"  {name}: {n} chunks")
        return

    if not args.collection:
        print("请指定 --collection NAME 或 --all")
        print("已有 archetype 目录:", list_archetype_collections())
        sys.exit(1)

    n = build_collection(args.collection, reset=args.reset)
    print(f"完成 {args.collection}: {n} chunks")


if __name__ == "__main__":
    main()
