#!/usr/bin/env python3
"""从教育部认可竞赛目录 PDF 提取 84 项比赛 → competitions_catalog_84.json"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF = ROOT / "data" / "competition-catalog-2025.pdf"
DEFAULT_OUT = ROOT / "data" / "competitions_catalog_84.json"


def extract_text(pdf_path: Path) -> str:
    parts: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return "\n".join(parts)


def parse_competitions(text: str) -> list[dict]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    items: list[dict] = []
    i = 0
    while i < len(lines):
        m = re.match(r"^(\d{1,2})[、.](.+)$", lines[i])
        if m:
            num = int(m.group(1))
            name = m.group(2).strip()
            url = ""
            if i + 1 < len(lines) and lines[i + 1].startswith("http"):
                url = lines[i + 1].strip()
                i += 1
            items.append(
                {
                    "id": num,
                    "name": name,
                    "official_url": url,
                    "archetype": "",
                    "aliases": [],
                }
            )
        i += 1
    return items


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    text = extract_text(args.pdf)
    items = parse_competitions(text)
    if len(items) != 84:
        print(f"警告: 解析到 {len(items)} 条，预期 84 条，请人工核对 PDF")

    payload = {
        "source_pdf": str(args.pdf.name),
        "source_url": "https://ifcen.sysu.edu.cn/sites/default/files/2026-01/2025%E5%B9%B4%E6%95%99%E8%82%B2%E9%83%A8%E8%AE%A4%E5%8F%AF%E7%9A%84%E5%85%A8%E5%9B%BD%E5%A4%A7%E5%AD%A6%E7%94%9F%E5%AD%A6%E7%A7%91%E7%AB%9E%E8%B5%9B%E7%9B%AE%E5%BD%95%E6%B8%85%E5%8D%95.pdf",
        "count": len(items),
        "competitions": items,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已写入 {args.out} ({len(items)} 项)")


if __name__ == "__main__":
    main()
