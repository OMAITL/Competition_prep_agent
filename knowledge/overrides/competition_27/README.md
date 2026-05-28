# 蓝桥杯全国软件和信息技术专业人才大赛（catalog id=27）补充

将大赛官网公布的章程、竞赛规则、科目说明等**粘贴为 Markdown** 放在本目录，重建索引后即可被 RAG 检索。

建议文件名：

- `rules-paste.md` — 章程与赛制摘录（已有初稿）
- `software-tracks.md` — 某届软件赛题型/分值补充（可选）

重建命令：

```powershell
python scripts/build_rag_index.py --collection competition_kb --reset
```
