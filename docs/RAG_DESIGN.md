# RAG 设计说明（竞赛备战 Agent）

## 1. RAG 在本项目里解决什么

| 问题 | 不用 RAG | 用 RAG |
|------|----------|--------|
| 赛题/章程太长 | 整页塞进 Prompt，易超长 | 只取相关片段 |
| 84 项资料分散 | 只靠 LLM 常识，易胡编 | 从你整理的文档里检索 |
| 同类比赛差异 | 仅 archetype 模板太粗 | 检索到该赛 override 文档 |

## 2. 检索发生在哪一步

```
用户选择 competition_id + 填写 Intake
    ↓
【RAG】用查询句检索知识库 → 得到 rag_context（Top-K 片段）
    ↓
【可选】抓取官网 → rules_text
    ↓
Prompt 1（注入 rag_context + rules_text）→ 赛题解析
    ↓
Prompt 2 → 路径规划
    ↓
【RAG】按 archetype 再检索「备赛资料/教程」类片段
    ↓
Prompt 3 + curated CSV + arXiv → 最终资料包
```

**两个检索点（推荐都做）：**

1. **检索点 A（Prompt 1 前）**：集合 `competition_kb`  
   - 查询：`{比赛名称} {archetype} 赛制 提交 评分`  
   - 来源：官方章程粘贴、override 文档、你整理的备赛笔记  

2. **检索点 B（Prompt 3 前）**：集合 `archetype_{archetype}`  
   - 查询：`{比赛名称} 学习路径 教程 入门`  
   - 来源：该赛道下的 Markdown/PDF 教程摘要  

## 3. 知识库怎么组织（不要 84 个库）

```
knowledge/
  shared/                    # 84 项通用：名录说明、备赛通用指南
    00-catalog-notes.md
  archetype_math_modeling/   # 数学建模赛道
    01-modeling-basics.md
    02-paper-writing.md
  archetype_algorithm_programming/
    ...
  overrides/                 # 单场加深（可选）
    competition_05/          # 对应 catalog id=5
      rules-paste.md
```

| 集合名（Chroma） | 内容 | 何时建索引 |
|------------------|------|------------|
| `competition_kb` | `shared/` + 所有 `overrides/` | `python scripts/build_rag_index.py --collection competition_kb` |
| `archetype_{name}` | 对应 `knowledge/archetype_{name}/` | `--collection archetype_math_modeling` |

## 4. 技术选型

| 组件 | 选型 | 说明 |
|------|------|------|
| 向量库 | **Chroma** | 本地持久化，零运维 |
| 切片 | 按段落 / 500 字重叠 80 | `rag/ingest.py` |
| 嵌入 | 优先 **本地** `paraphrase-multilingual-MiniLM-L12-v2` | 中文友好、免 Embedding API |
| 备选嵌入 | OpenAI 兼容 `text-embedding-3-small` | `.env` 设 `EMBEDDING_MODEL=openai` |

## 5. 环境变量

```env
# LLM（生成）
LLM_API_KEY=
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# RAG（检索，可选）
RAG_TOP_K=5
EMBEDDING_BACKEND=local
# EMBEDDING_BACKEND=openai
# OPENAI_API_KEY=  # 与 LLM 可相同 key
```

## 6. 常用命令

```powershell
pip install -r requirements.txt

# 首次：下载本地嵌入模型（需联网，约 400MB）
python scripts/build_rag_index.py --all

# 只重建数学建模赛道
python scripts/build_rag_index.py --collection archetype_math_modeling

# 试检索
python scripts/query_rag.py --query "全国大学生数学建模竞赛 赛制" --collection competition_kb
```

## 7. 与 Prompt 的衔接

在 Prompt 1 / 3 中增加变量 `{{rag_context}}`，格式示例：

```text
【知识库检索结果（请优先采信，勿与其中事实冲突）】
[1] (source: knowledge/archetype_math_modeling/01-modeling-basics.md)
......片段......

[2] (source: overrides/competition_05/rules-paste.md)
......片段......
```

见 `docs/competition-prep-prompts.md` 末尾「RAG 增补」。

## 8. 简历可写

> 为竞赛备战 Agent 构建 **RAG 知识库**：按 12 类赛道与单场 override 切片入库；检索增强赛题解析与资料推荐，降低幻觉；Chroma + 多语言向量检索，Top-K 注入 Prompt。
