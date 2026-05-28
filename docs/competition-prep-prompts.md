# 竞赛备战规划 Agent — 核心 Prompt 骨架（v0.1）

> 使用方式：按顺序调用 Prompt 1 → 2 → 3；每步 **只输出 JSON**，`temperature=0.2`  
> 将上一步 JSON 作为 `{{previous_output}}` 传入下一步。

---

## 全局 System Prompt（三条共用）

```text
你是「竞赛备战规划」助手，面向大学生竞赛备赛场景。

硬性规则：
1. 只输出合法 JSON，不要 Markdown 代码块外的任何解释。
2. 禁止编造 URL、arxiv ID、DOI。若不确定链接，设 verified=false 且 url=""。
3. 路径必须考虑用户截止日期与每周可投入小时数，阶段数 4-6 个。
4. 验收标准必须可执行、可判断（避免「认真学习」等空话）。
5. 资料优先官方与 curated 列表；社区内容标注 tier=community。
6. 若赛题信息不足，在 JSON 的 warnings 数组说明缺什么，不要猜测赛制。

语言：JSON 内字符串使用简体中文，paper_search_keywords 使用英文。
```

---

## Prompt 1：赛题解析

**输入变量**
- `{{competition_name}}`
- `{{competition_template_id}}`
- `{{official_url}}`
- `{{rules_text}}`（官网摘要或用户粘贴全文）
- `{{track}}`
- `{{skill_level}}`

**User Prompt 模板**

```text
请根据以下比赛信息，输出 competition_analysis JSON。

比赛名称：{{competition_name}}
模板类型：{{competition_template_id}}
官方链接：{{official_url}}
赛道：{{track}}
用户水平：{{skill_level}}

赛题/章程原文或摘要：
---
{{rules_text}}
---

输出 JSON 结构（字段必须齐全）：
{
  "warnings": ["string"],
  "competition_analysis": {
    "summary": "200字以内赛题摘要",
    "format": "赛制与流程",
    "scoring": ["评分维度1", "..."],
    "deliverables": ["提交物1", "..."],
    "required_skills": [
      {
        "name": "技能名",
        "priority": "must|should|nice",
        "description": "赛题为何需要"
      }
    ],
    "common_pitfalls": ["坑1", "..."],
    "paper_search_keywords": ["english keyword1", "..."]
  }
}

要求：
- required_skills 至少 5 项，含 must 至少 3 项。
- paper_search_keywords 3-5 个英文词，可用于 arXiv 检索。
- 信息不足时 warnings 说明，但仍基于已有文本合理推断，勿虚构具体日期/奖金。
```

---

## Prompt 2：分阶段备战路径

**输入变量**
- `{{competition_analysis}}`（Prompt1 的 JSON 字符串）
- `{{deadline}}`
- `{{weekly_hours}}`
- `{{skill_level}}`
- `{{self_assessed_skills}}`
- `{{goal}}`

**User Prompt 模板**

```text
基于赛题解析结果，为用户生成分阶段备战路径。

赛题解析：
{{competition_analysis}}

用户约束：
- 截止日期：{{deadline}}
- 每周可投入小时：{{weekly_hours}}
- 水平：{{skill_level}}
- 自评已有技能：{{self_assessed_skills}}
- 目标：{{goal}}

请计算从今日到截止日的剩余周数（向上取整），输出 prep_plan JSON：
{
  "prep_plan": {
    "total_weeks": 6,
    "phases": [
      {
        "phase_id": 1,
        "title": "阶段标题",
        "week_range": "W1-W2",
        "goals": ["目标1"],
        "skills": ["技能点"],
        "estimated_hours": 20,
        "acceptance_criteria": ["可验证标准1"],
        "risks": ["风险与应对"]
      }
    ],
    "weekly_summary": [
      { "week": 1, "focus": "本周重点", "tasks": ["任务1", "任务2"] }
    ]
  },
  "skill_gap": {
    "gaps": [
      {
        "skill": "技能名",
        "current_level": "none|basic|proficient",
        "required_level": "basic|proficient|expert",
        "action": "具体补齐动作"
      }
    ],
    "strengths": ["已有优势"],
    "priority_actions": ["本周最优先3-5件事"]
  },
  "submission_checklist": [
    {
      "item": "提交项",
      "due_phase_id": 4,
      "tips": "注意事项"
    }
  ]
}

要求：
- phases 数量 4-6；各阶段 estimated_hours 之和约等于 total_weeks * weekly_hours（允许±15%）。
- 最后一阶段必须预留「整合、测试、答辩/提交」时间。
- acceptance_criteria 每条可在一周内验证是否完成。
- submission_checklist 至少 6 项，与 deliverables 对齐。
```

---

## Prompt 3：资料合并与论文筛选

**输入变量**
- `{{competition_analysis}}`
- `{{prep_plan}}`
- `{{skill_gap}}`
- `{{curated_resources}}`（CSV/JSON 列表，含 title, url, tier, tags）
- `{{arxiv_candidates}}`（API 返回的原始列表，可为空数组）

**User Prompt 模板**

```text
请为备赛用户生成最终资料包 resources 与 papers，合并以下来源，禁止编造链接。

赛题解析：
{{competition_analysis}}

路径规划：
{{prep_plan}}

能力差距：
{{skill_gap}}

人工 curated 资料（优先使用，verified=true）：
{{curated_resources}}

arXiv API 候选（仅可从中选择，勿新增未列出论文）：
{{arxiv_candidates}}

输出 JSON：
{
  "resources": [
    {
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
    }
  ],
  "papers": [
    {
      "title": "",
      "authors": "",
      "year": 2024,
      "arxiv_id": "",
      "url": "",
      "relevance_reason": "",
      "read_priority": "must|should|optional",
      "related_phase_ids": [2],
      "verified": true
    }
  ]
}

数量要求：
- resources 总数 15-25 条；must_read 6-10 条；official tier 至少 3 条（若无则 verified=false 并说明）。
- papers 3-5 篇，必须来自 arxiv_candidates；若无候选则 papers=[]。
- 每条 resource 必须关联至少一个 phase_id。
- llm_suggested 的资源若无可靠 url，verified=false，url=""。

排序：按 phase_id 升序，同阶段内 must_read 在前。
```

---

## 调用示例（伪代码）

```python
# 1. 可选：抓取 official_url 纯文本 → rules_text
# 2. out1 = call_llm(PROMPT_1, ...)
# 3. keywords = out1["competition_analysis"]["paper_search_keywords"]
# 4. arxiv_candidates = arxiv_search(keywords, max_results=10)
# 5. out2 = call_llm(PROMPT_2, competition_analysis=json.dumps(out1), ...)
# 6. out3 = call_llm(PROMPT_3, ..., curated_resources=load_csv(), arxiv_candidates=...)
# 7. package = merge_meta(out1, out2, out3)
# 8. export_markdown(package)
```

---

## Curated CSV 模板（`data/curated_resources.csv`）

```csv
resource_id,title,url,tier,type,tags,estimated_minutes,priority
r001,赛题官方页面,https://example.com/official,official,doc,"baseline",30,must_read
r002,Python 数据分析入门,https://example.com/tutorial,course,tutorial,"python,data",120,recommended
```

---

## Markdown 导出模板（`export.py` 可参考）

```markdown
# {{meta.competition_name}} 备战规划

> 截止：{{meta.deadline}} | 剩余 {{meta.weeks_remaining}} 周 | 每周 {{meta.weekly_hours}} 小时

## 赛题摘要
{{competition_analysis.summary}}

## 分阶段路径
{{#each prep_plan.phases}}
### 阶段 {{phase_id}}：{{title}}（{{week_range}}）
- **目标**：...
- **验收标准**：...
{{/each}}

## 必读资料
...

## 推荐论文
...

## 提交 Checklist
- [ ] ...

---
*{{meta.disclaimer}}*
```

---

## RAG 增补（检索增强）

在调用 Prompt 1 / 3 **之前**执行检索，将结果填入 `{{rag_context}}`。

```python
from rag.retrieve import (
    retrieve_for_competition,
    merge_retrieval_results,
    format_rag_context,
)

hits = retrieve_for_competition(competition_name, archetype)
rag_context = format_rag_context(merge_retrieval_results(hits))
```

### Prompt 1 增加段落（放在赛题原文之后）

```text
【知识库检索结果（优先采信；与官网冲突时以官网为准）】
{{rag_context}}
```

### Prompt 3 增加段落

```text
【知识库中的备赛资料片段（可补充 curated，禁止编造其中未出现的 URL）】
{{rag_context}}
```

### System Prompt 增补一条

```text
7. 若提供 rag_context，其中事实优先于模型臆测；仍禁止编造 rag_context 中未出现的链接。
```

索引构建见 `docs/RAG_DESIGN.md` 与 `python scripts/build_rag_index.py --all`。

---

## 自检清单（上线前）

- [ ] 20 条评测输入跑通，无 JSON 解析失败
- [ ] 抽检 20 条输出链接，胡编率 < 5%
- [ ] RAG 索引已构建，`query_rag.py` 能命中示例文档
- [ ] 总时长 < 90s（或说明瓶颈在论文 API）
- [ ] 10 人试用问卷回收 ≥ 8 份
