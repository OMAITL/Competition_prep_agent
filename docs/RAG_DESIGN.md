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
【检索点 A】Prompt 1 前 → rag_context_analysis
    ↓
【可选】抓取官网 → rules_text
    ↓
Prompt 1（rag_context + rules_text + catalog）→ competition_analysis（具体比赛解析）
    ↓
【检索点 A′】Prompt 2 前 → rag_context_prep（可选，与 A 可复用缓存）
    ↓
Prompt 2（competition_analysis + rag_context_prep + 用户 Intake）→ prep_plan
    ↓
【检索点 B】Prompt 3 前 → rag_context_resources
    ↓
Prompt 3 + curated CSV + arXiv → 最终资料包
```

### Prompt 2 靠什么「具体比赛」规划？

**不是只靠 archetype。** 路径规划的信息来源优先级：

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1 | `competition_analysis`（Prompt 1 输出） | 已含该赛的赛制、提交物、能力要求 |
| 2 | `rules_text` / 官网摘要 | 当年最新规则 |
| 3 | 检索点 A′ → `competition_kb` | override、shared 中与「阶段/里程碑/提交清单」相关片段 |
| 4 | 检索点 A′ → `archetype_*` | 同类赛的通用阶段骨架（补充，非主依据） |
| 5 | 用户 Intake | deadline、weekly_hours、goal 等倒排 |

archetype 在 Prompt 2 中只是**补充**；若 Prompt 1 信息不足且无 override，路径会变泛——应优先补 `overrides/competition_{id}/` 或让用户粘贴 `rules_text`。

## 3. 三个检索点

1. **检索点 A（Prompt 1 前）** — 赛题解析  
   - 集合：`competition_kb` + `archetype_{archetype}`  
   - 查询后缀：`赛制 规则 提交 评分`  
   - 代码：`build_rag_context_for_prompt1()`

2. **检索点 A′（Prompt 2 前，推荐）** — 路径规划  
   - 集合：`competition_kb`（主）+ `archetype_{archetype}`（辅）  
   - 查询后缀：`备赛路径 阶段 里程碑 提交清单`  
   - 代码：`build_rag_context_for_prompt2()`  
   - 可与 A 合并缓存，避免重复 embedding 查询

3. **检索点 B（Prompt 3 前）** — 资料推荐  
   - 集合：`competition_kb` + `archetype_{archetype}`  
   - 查询后缀：`资料 教程 工具 开源 入门`  
   - 代码：`build_rag_context_for_prompt3()`

## 4. 知识库怎么组织（不要 84 个库）

```
knowledge/
  shared/                    # 84 项通用：名录说明、备赛通用指南
    00-catalog-notes.md
  archetype_math_modeling/   # 数学建模赛道
    01-modeling-basics.md
  archetype_algorithm_programming/
    ...
  overrides/                 # 单场加深（Prompt 1 / 2 的关键差异来源）
    competition_05/
      rules-paste.md
```

| 集合名（Chroma） | 内容 | 何时建索引 |
|------------------|------|------------|
| `competition_kb` | `shared/` + 所有 `overrides/` | `--collection competition_kb` |
| `archetype_{name}` | 对应 `knowledge/archetype_{name}/` | `--collection archetype_math_modeling` |

## 5. 技术选型

| 组件 | 选型 | 说明 |
|------|------|------|
| 向量库 | **Chroma** | 本地持久化，零运维 |
| 切片 | 按段落 / 500 字重叠 80 | `rag/ingest.py` |
| 嵌入 | 优先 **本地** `paraphrase-multilingual-MiniLM-L12-v2` | 中文友好、免 Embedding API |
| 备选嵌入 | OpenAI 兼容 `text-embedding-3-small` | `.env` 设 `EMBEDDING_BACKEND=openai` |

## 6. 环境变量

```env
RAG_TOP_K=5
EMBEDDING_BACKEND=local
HF_ENDPOINT=https://hf-mirror.com
```

## 7. 常用命令

```powershell
python scripts/build_rag_index.py --all --reset
python scripts/query_rag.py --name "全国大学生数学建模竞赛" --archetype math_modeling --query test
```

## 8. 与 Prompt 的衔接

| Prompt | 变量 | 检索函数 |
|--------|------|----------|
| 1 | `{{rag_context}}` | `build_rag_context_for_prompt1()` |
| 2 | `{{rag_context}}`（可选） | `build_rag_context_for_prompt2()` |
| 3 | `{{rag_context}}` | `build_rag_context_for_prompt3()` |

格式示例：

```text
【知识库检索结果（请优先采信，勿与其中事实冲突）】
[1] (source: overrides/competition_05/rules-paste.md)
......片段......
```

见 `docs/competition-prep-prompts.md` 末尾「RAG 增补」。
