# 数据目录说明

## 已纳入版本库

| 文件 | 说明 |
|------|------|
| `competitions_catalog_84.json` | 84 项结构化名录（id / name / official_url / archetype） |
| `curated_resources.example.csv` | 资料推荐 CSV 格式示例 |

## 仅本地使用（不提交 GitHub）

| 文件 | 说明 |
|------|------|
| `competition-catalog-2025.pdf` | 高教学会竞赛目录 PDF，请自行下载后放入此目录 |
| `catalog-raw.txt` | 运行 `extract_catalog_from_pdf.py` 时生成的中间文本 |

PDF 来源可参考脚本内 `source_url` 字段，或各校教务处转载的「教育部认可竞赛目录」。

重新从 PDF 解析：

```powershell
# 先将 PDF 放到 data/competition-catalog-2025.pdf
python scripts/extract_catalog_from_pdf.py
python scripts/assign_archetypes.py
```

## 向量索引（不提交）

`data/chroma/` 由 `python scripts/build_rag_index.py --all` 本地生成，clone 后需自行建索引。
