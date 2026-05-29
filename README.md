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

- `data/competitions_catalog_84.json` — 84 项结构化名录（名称 + 官网）
- `data/README.md` — PDF 等本地文件说明（**PDF 不提交 GitHub**）

## 生成备战包（Prompt 1→2→3）

```powershell
# 数学建模 id=5（默认）
python scripts/generate_prep.py --id 5

# 蓝桥杯 id=27
python scripts/generate_prep.py --id 27 --goal "省赛进入前30%"

# 输出在 output/prep_{id}.md 与 output/prep_{id}.json
```

需已在 `.env` 配置 DeepSeek；首次请先 `build_rag_index.py --all`。

## Vue 前端（C 端产品）

前后端分离：**FastAPI** 提供 API，**Vue 3 + Element Plus** 提供界面。

### 开发模式（推荐）

终端 1 — 启动 API：

```powershell
cd c:\Users\JimiM\Desktop\grade_first\agent
pip install -r requirements.txt
python -m uvicorn backend.api.main:app --reload --host 127.0.0.1 --port 8000
```

终端 2 — 启动前端：

```powershell
cd c:\Users\JimiM\Desktop\grade_first\agent\frontend
npm install
npm run dev
```

浏览器打开 `http://127.0.0.1:5173`。或双击 `scripts/run_web_dev.bat`（Windows）。

### 生产模式（单端口）

```powershell
cd frontend && npm install && npm run build
cd ..
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000
```

访问 `http://127.0.0.1:8000`（API 同时托管 `frontend/dist` 静态资源）。

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
