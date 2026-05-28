#!/usr/bin/env python3
"""按比赛名称关键词为 84 项分配 archetype（初稿，需人工抽检）。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "competitions_catalog_84.json"

# archetype → 关键词（按优先级从上到下匹配）
RULES: list[tuple[str, list[str]]] = [
    ("algorithm_programming", ["ACM", "程序设计", "蓝桥杯", "百度之星", "码蹄杯", "软件杯", "计算机系统能力"]),
    ("math_modeling", ["数学建模", "统计建模"]),
    ("robotics_engineering", ["机器人", "Robo", "智能汽车", "智能制造", "西门子杯", "睿抗", "ICT"]),
    ("innovation_entrepreneurship", ["创新大赛", "挑战杯", "互联网", "创新创业", "iCAN", "服务外包", "三创"]),
    ("ai_data", ["人工智能", "算法精英", "大数据"]),
    ("design_creative", ["设计", "广告", "艺术", "华灿", "米兰", "数字艺术", "媒体", "花园"]),
    ("business_simulation", ["商业", "沙盘", "企业竞争", "物流", "电子商务", "金融", "财会", "税收", "市场调查"]),
    ("language_humanities", ["英语", "外语", "演讲", "经典诵", "跨文化"]),
    ("medical_life", ["医学", "生命科学", "金相", "基础医学"]),
    ("physics_chemistry", ["物理", "化学", "化工", "力学", "材料"]),
    ("electronics_embedded", ["电子设计", "嵌入式", "集成电路", "光电", "信息安全"]),
    ("mechanical_structure", ["机械", "结构", "成图", "三维数字化", "工业设计"]),
]


def assign(name: str) -> str:
    for archetype, keywords in RULES:
        if any(k in name for k in keywords):
            return archetype
    return "general_stem"


def main() -> None:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    for c in data["competitions"]:
        c["archetype"] = assign(c["name"])
    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    counts: dict[str, int] = {}
    for c in data["competitions"]:
        counts[c["archetype"]] = counts.get(c["archetype"], 0) + 1
    print("archetype 分布:", counts)


if __name__ == "__main__":
    main()
