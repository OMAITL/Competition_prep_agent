# 教育部 84 项学科竞赛 · 备战规划 Agent

## 快速开始

```powershell
cd c:\Users\JimiM\Desktop\grade_first\agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/extract_catalog_from_pdf.py
python scripts/assign_archetypes.py
```

详细步骤见：**[docs/GETTING_STARTED_84_COMPETITIONS.md](docs/GETTING_STARTED_84_COMPETITIONS.md)**

## 数据

- `data/competition-catalog-2025.pdf` — 官方目录 PDF
- `data/competitions_catalog_84.json` — 84 项结构化名录（名称 + 官网）

## RAG（检索增强）

```powershell
pip install -r requirements.txt
python scripts/build_rag_index.py --all
python scripts/query_rag.py --name "全国大学生数学建模竞赛" --archetype math_modeling --query test
```

- 设计说明：[docs/RAG_DESIGN.md](docs/RAG_DESIGN.md)
- 知识库目录：`knowledge/`（往里面加 `.md` 后重新 `--all` 建索引）

## 文档

- [84 项启动指南](docs/GETTING_STARTED_84_COMPETITIONS.md)
- [RAG 设计](docs/RAG_DESIGN.md)
- [PRD](docs/competition-prep-agent-PRD.md)
- [Prompt 骨架](docs/competition-prep-prompts.md)
