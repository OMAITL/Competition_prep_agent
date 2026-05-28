# 全国大学生数学建模竞赛（catalog id=5）补充

将当年赛题说明、校赛通知、评分细则等**粘贴为 Markdown** 放在本目录，重建索引后即可被 RAG 检索。

建议文件名：

- `2026-rules-paste.md` — 组委会章程摘录
- `school-notice.md` — 本校报名与培训安排

重建命令：

```powershell
python scripts/build_rag_index.py --collection competition_kb --reset
```
