#!/usr/bin/env python3
"""Prompt 1→2→3 最小流水线：catalog + RAG + DeepSeek → 备战包。"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from openai import OpenAI

from rag.pipeline_hook import (
    build_rag_context_for_prompt1,
    build_rag_context_for_prompt2,
    build_rag_context_for_prompt3,
)

load_dotenv(ROOT / ".env")

CATALOG = ROOT / "data" / "competitions_catalog_84.json"
CURATED_DIR = ROOT / "data" / "curated"
OUTPUT_DIR = ROOT / "output"

SYSTEM_PROMPT = """你是「竞赛备战规划」助手，面向大学生竞赛备赛场景。

硬性规则：
1. 只输出合法 JSON，不要 Markdown 代码块外的任何解释。
2. 禁止编造 URL、arxiv ID、DOI。若不确定链接，设 verified=false 且 url=""。
3. 路径必须考虑用户截止日期与每周可投入小时数，阶段数 4-6 个。
4. 验收标准必须可执行、可判断（避免「认真学习」等空话）。
5. 资料优先官方与 curated 列表；社区内容标注 tier=community。
6. 若赛题信息不足，在 JSON 的 warnings 数组说明缺什么，不要猜测赛制。
7. 若提供 rag_context，其中事实优先于模型臆测；仍禁止编造 rag_context 中未出现的链接。
8. Prompt 2 的路径须与 competition_analysis 中的具体比赛一致，不得仅按 archetype 泛化。

语言：JSON 内字符串使用简体中文，paper_search_keywords 使用英文。"""


def load_catalog() -> list[dict]:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    return data["competitions"]


def load_catalog_entry(competition_id: int) -> dict:
    for c in load_catalog():
        if c["id"] == competition_id:
            return c
    raise ValueError(f"catalog 中未找到 id={competition_id}")


def load_curated(archetype: str) -> list[dict]:
    path = CURATED_DIR / f"{archetype}.csv"
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(dict(row))
    return rows


def weeks_until(deadline: str) -> int:
    d = date.fromisoformat(deadline)
    today = date.today()
    days = (d - today).days
    if days <= 0:
        return 1
    return max(1, (days + 6) // 7)


def extract_json(text: str) -> dict:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def call_llm(client: OpenAI, model: str, user_prompt: str) -> dict:
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    content = resp.choices[0].message.content or ""
    try:
        return extract_json(content)
    except json.JSONDecodeError as e:
        print("LLM 返回非 JSON，原文片段：", content[:500], file=sys.stderr)
        raise SystemExit(f"JSON 解析失败: {e}") from e


def build_prompt1(
    entry: dict,
    *,
    rules_text: str,
    rag_context: str,
    track: str,
    skill_level: str,
) -> str:
    rules = rules_text.strip() or "（用户未提供章程；请主要依据知识库检索结果，不足处写入 warnings）"
    return f"""请根据以下比赛信息，输出 competition_analysis JSON。

比赛名称：{entry['name']}
模板类型：{entry['archetype']}
官方链接：{entry.get('official_url') or '（待补充）'}
赛道：{track or '默认'}
用户水平：{skill_level}

赛题/章程原文或摘要：
---
{rules}
---

【知识库检索结果（优先采信；与官网冲突时以官网为准）】
{rag_context}

输出 JSON 结构（字段必须齐全）：
{{
  "warnings": ["string"],
  "competition_analysis": {{
    "summary": "200字以内赛题摘要",
    "format": "赛制与流程",
    "scoring": ["评分维度1"],
    "deliverables": ["提交物1"],
    "required_skills": [
      {{"name": "技能名", "priority": "must|should|nice", "description": "赛题为何需要"}}
    ],
    "common_pitfalls": ["坑1"],
    "paper_search_keywords": ["english keyword1"]
  }}
}}

要求：
- required_skills 至少 5 项，含 must 至少 3 项。
- paper_search_keywords 3-5 个英文词。
- 信息不足时 warnings 说明，勿虚构具体日期/奖金。"""


def build_prompt2(
    entry: dict,
    out1: dict,
    *,
    rag_context: str,
    deadline: str,
    weekly_hours: int,
    skill_level: str,
    self_skills: str,
    goal: str,
) -> str:
    analysis_json = json.dumps(out1, ensure_ascii=False, indent=2)
    return f"""基于赛题解析结果，为用户生成分阶段备战路径。

比赛名称：{entry['name']}

赛题解析（优先采信，须与具体比赛对齐，勿泛化为赛道模板）：
{analysis_json}

【知识库检索结果（可选，补充阶段/里程碑/提交清单）】
{rag_context}

用户约束：
- 截止日期：{deadline}
- 每周可投入小时：{weekly_hours}
- 水平：{skill_level}
- 自评已有技能：{self_skills or '未填写'}
- 目标：{goal or '完成备赛并提交'}

请计算从今日到截止日的剩余周数（向上取整），输出 prep_plan JSON：
{{
  "prep_plan": {{
    "total_weeks": 6,
    "phases": [
      {{
        "phase_id": 1,
        "title": "阶段标题",
        "week_range": "W1-W2",
        "goals": ["目标1"],
        "skills": ["技能点"],
        "estimated_hours": 20,
        "acceptance_criteria": ["可验证标准1"],
        "risks": ["风险与应对"]
      }}
    ],
    "weekly_summary": [
      {{ "week": 1, "focus": "本周重点", "tasks": ["任务1"] }}
    ]
  }},
  "skill_gap": {{
    "gaps": [{{"skill": "技能名", "current_level": "none", "required_level": "basic", "action": "动作"}}],
    "strengths": ["已有优势"],
    "priority_actions": ["本周最优先3-5件事"]
  }},
  "submission_checklist": [
    {{ "item": "提交项", "due_phase_id": 4, "tips": "注意事项" }}
  ]
}}

要求：
- phases 数量 4-6；各阶段 estimated_hours 之和约等于 total_weeks * weekly_hours（允许±15%）。
- 最后一阶段必须预留整合、测试、答辩/提交时间。
- submission_checklist 至少 6 项。"""


def build_prompt3(
    out1: dict,
    out2: dict,
    *,
    rag_context: str,
    curated: list[dict],
) -> str:
    return f"""请为备赛用户生成最终资料包 resources 与 papers，合并以下来源，禁止编造链接。

赛题解析：
{json.dumps(out1, ensure_ascii=False, indent=2)}

路径规划：
{json.dumps(out2.get('prep_plan', {}), ensure_ascii=False, indent=2)}

能力差距：
{json.dumps(out2.get('skill_gap', {}), ensure_ascii=False, indent=2)}

人工 curated 资料（优先使用，verified=true）：
{json.dumps(curated, ensure_ascii=False, indent=2)}

arXiv API 候选（本版本为空，papers 必须输出 []）：
[]

【知识库中的备赛资料片段（可补充 curated，禁止编造其中未出现的 URL）】
{rag_context}

输出 JSON：
{{
  "resources": [
    {{
      "resource_id": "r001",
      "title": "",
      "tier": "official|course|community|paper",
      "type": "doc|video|repo|tutorial|paper|tool",
      "url": "",
      "reason": "推荐理由，50字内",
      "estimated_minutes": 60,
      "phase_ids": [1, 2],
      "priority": "must_read|recommended|optional",
      "verified": true,
      "source": "curated|llm_suggested|arxiv"
    }}
  ],
  "papers": []
}}

数量要求：
- resources 总数 12-20 条；must_read 至少 5 条；优先使用 curated 列表中的 URL。
- papers 必须为空数组 []。
- 每条 resource 必须关联至少一个 phase_id。
- 无可靠 url 时 verified=false，url=""。"""


def merge_package(
    entry: dict,
    out1: dict,
    out2: dict,
    out3: dict,
    *,
    deadline: str,
    weekly_hours: int,
    skill_level: str,
) -> dict:
    analysis = out1.get("competition_analysis", out1)
    return {
        "meta": {
            "plan_id": str(uuid.uuid4()),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "prompt_version": "v0.1",
            "competition_name": entry["name"],
            "competition_id": entry["id"],
            "competition_template_id": entry["archetype"],
            "deadline": deadline,
            "weeks_remaining": weeks_until(deadline),
            "weekly_hours": weekly_hours,
            "skill_level": skill_level,
            "disclaimer": "本方案仅供参考，请以官方赛题与章程为准。",
        },
        "warnings": out1.get("warnings", []),
        "competition_analysis": analysis,
        "prep_plan": out2.get("prep_plan", {}),
        "skill_gap": out2.get("skill_gap", {}),
        "submission_checklist": out2.get("submission_checklist", []),
        "resources": out3.get("resources", []),
        "papers": out3.get("papers", []),
    }


def export_markdown(pkg: dict) -> str:
    meta = pkg["meta"]
    ca = pkg["competition_analysis"]
    lines = [
        f"# {meta['competition_name']} 备战规划",
        "",
        f"> 截止：{meta['deadline']} | 剩余约 {meta['weeks_remaining']} 周 | "
        f"每周 {meta['weekly_hours']} 小时 | 水平：{meta['skill_level']}",
        "",
    ]
    if pkg.get("warnings"):
        lines += ["## 提示", ""] + [f"- {w}" for w in pkg["warnings"]] + [""]

    lines += ["## 赛题摘要", "", ca.get("summary", ""), "", "## 赛制与流程", "", ca.get("format", ""), ""]

    lines += ["", "## 评分维度", ""] + [f"- {s}" for s in ca.get("scoring", [])]
    lines += ["", "## 提交物", ""] + [f"- {d}" for d in ca.get("deliverables", [])]

    lines += ["", "## 分阶段路径", ""]
    for ph in pkg.get("prep_plan", {}).get("phases", []):
        lines.append(f"### 阶段 {ph.get('phase_id')}：{ph.get('title')}（{ph.get('week_range')}）")
        lines.append(f"- **预计小时**：{ph.get('estimated_hours')}")
        for g in ph.get("goals", []):
            lines.append(f"- **目标**：{g}")
        for ac in ph.get("acceptance_criteria", []):
            lines.append(f"- **验收**：{ac}")
        lines.append("")

    lines += ["## 必读资料", ""]
    for r in pkg.get("resources", []):
        if r.get("priority") != "must_read":
            continue
        url = r.get("url") or "（链接待补充）"
        v = "✓" if r.get("verified") else "?"
        lines.append(f"- [{v}] [{r.get('title')}]({url}) — {r.get('reason', '')}")

    lines += ["", "## 推荐资料", ""]
    for r in pkg.get("resources", []):
        if r.get("priority") == "must_read":
            continue
        url = r.get("url") or "（链接待补充）"
        lines.append(f"- [{r.get('title')}]({url}) — {r.get('reason', '')}")

    lines += ["", "## 提交 Checklist", ""]
    for item in pkg.get("submission_checklist", []):
        lines.append(f"- [ ] {item.get('item')}（阶段 {item.get('due_phase_id')}）— {item.get('tips', '')}")

    lines += ["", "---", f"*{meta.get('disclaimer', '')}*"]
    return "\n".join(lines)


ProgressCallback = Callable[[str, str], None]


@dataclass
class PrepGenerationOptions:
    competition_id: int
    deadline: str
    weekly_hours: int
    skill_level: str
    goal: str = ""
    self_skills: str = ""
    rules_text: str = ""
    track: str = ""
    no_rag: bool = False


def _notify(progress: ProgressCallback | None, stage: str, message: str) -> None:
    if progress:
        progress(stage, message)


def generate_prep_package(
    options: PrepGenerationOptions,
    *,
    progress: ProgressCallback | None = None,
) -> tuple[dict, str]:
    """执行 Prompt 1→2→3，返回 (完整 JSON 包, Markdown 文本)。"""
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("LLM_MODEL", "deepseek-chat")
    if not api_key:
        raise RuntimeError("请在 .env 中设置 LLM_API_KEY")

    entry = load_catalog_entry(options.competition_id)
    name = entry["name"]
    archetype = entry["archetype"]
    curated = load_curated(archetype)

    _notify(progress, "准备", f"{name}（id={options.competition_id}，{archetype}）")

    if options.no_rag:
        rag1 = rag2 = rag3 = "（已跳过 RAG）"
    else:
        _notify(progress, "RAG", "检索知识库…")
        rag1 = build_rag_context_for_prompt1(name, archetype, track=options.track)
        rag2 = build_rag_context_for_prompt2(name, archetype, goal=options.goal)
        rag3 = build_rag_context_for_prompt3(name, archetype)

    client = OpenAI(api_key=api_key, base_url=base_url)

    _notify(progress, "Prompt 1", "赛题解析…")
    out1 = call_llm(client, model, build_prompt1(
        entry, rules_text=options.rules_text, rag_context=rag1,
        track=options.track, skill_level=options.skill_level,
    ))

    _notify(progress, "Prompt 2", "路径规划…")
    out2 = call_llm(client, model, build_prompt2(
        entry, out1, rag_context=rag2, deadline=options.deadline,
        weekly_hours=options.weekly_hours, skill_level=options.skill_level,
        self_skills=options.self_skills, goal=options.goal,
    ))

    _notify(progress, "Prompt 3", "资料推荐…")
    out3 = call_llm(client, model, build_prompt3(
        out1, out2, rag_context=rag3, curated=curated,
    ))

    pkg = merge_package(
        entry, out1, out2, out3,
        deadline=options.deadline,
        weekly_hours=options.weekly_hours,
        skill_level=options.skill_level,
    )
    _notify(progress, "完成", "备战包已生成")
    return pkg, export_markdown(pkg)


def main() -> None:
    parser = argparse.ArgumentParser(description="生成竞赛备战包（Prompt 1→2→3）")
    parser.add_argument("--id", type=int, default=5, help="catalog 比赛 id，默认 5 数学建模")
    parser.add_argument("--deadline", default="2026-09-10", help="截止日期 YYYY-MM-DD")
    parser.add_argument("--weekly-hours", type=int, default=10)
    parser.add_argument("--skill-level", default="intermediate", choices=["beginner", "intermediate", "experienced"])
    parser.add_argument("--goal", default="完成校赛选拔并提交合格论文")
    parser.add_argument("--track", default="")
    parser.add_argument("--self-skills", default="Python, 高等数学")
    parser.add_argument("--rules-text", default="", help="可选：粘贴章程原文")
    parser.add_argument("--output", default="", help="输出 Markdown 路径，默认 output/prep_{id}.md")
    parser.add_argument("--json", default="", help="可选：同时保存完整 JSON")
    parser.add_argument("--no-rag", action="store_true", help="跳过 RAG（调试用）")
    args = parser.parse_args()

    def _cli_progress(stage: str, message: str) -> None:
        print(f"[{stage}] {message}")

    pkg, _md = generate_prep_package(
        PrepGenerationOptions(
            competition_id=args.id,
            deadline=args.deadline,
            weekly_hours=args.weekly_hours,
            skill_level=args.skill_level,
            goal=args.goal,
            self_skills=args.self_skills,
            rules_text=args.rules_text,
            track=args.track,
            no_rag=args.no_rag,
        ),
        progress=_cli_progress,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = Path(args.output) if args.output else OUTPUT_DIR / f"prep_{args.id}.md"
    md_path.write_text(_md, encoding="utf-8")
    print(f"[6/6] 已写入 Markdown：{md_path}")

    if args.json:
        json_path = Path(args.json)
    else:
        json_path = OUTPUT_DIR / f"prep_{args.id}.json"
    json_path.write_text(json.dumps(pkg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"      已写入 JSON：{json_path}")


if __name__ == "__main__":
    main()
