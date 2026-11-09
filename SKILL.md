---
name: ICTYSearcher
description: 独立检索前南斯拉夫问题国际刑事法庭（ICTY）官网，查找案件页、新闻稿和公开遗产文书；支持站点搜索、页面正文读取和 PDF 文本提取。
---

# ICTYSearcher

> **`<skill-dir>`** = 本 SKILL.md 所在目录。核心脚本为 `<skill-dir>/scripts/icty_search.py`；Windows 用 `<skill-dir>/run.ps1`，macOS/Linux 用 `<skill-dir>/run.sh`。部署与排错见 [README.md](README.md)。

这个 skill 只做 `icty.org` 一个站点：

- `search`：调用站内 `search-results?as_q=`，返回案件页、新闻稿和其他公开页面；
- `fetch`：读取案件页/新闻页正文，或下载并提取 PDF；
- `doctor`：探测站内搜索。

## 命令

```powershell
& '<skill-dir>/run.ps1' search 'Karadzic' --limit 10 --out './icty-search.json'
& '<skill-dir>/run.ps1' search 'command responsibility' --limit 10
& '<skill-dir>/run.ps1' fetch 'https://www.icty.org/en/case/karadzic' --out './icty-case.json' --text-out './icty-case.txt'
& '<skill-dir>/run.ps1' fetch 'https://www.icty.org/...pdf' --pdf-out './icty.pdf' --text-out './icty.txt'
& '<skill-dir>/run.ps1' doctor
```

通用参数：`--out`、`--cache`、`--cache-ttl`、`--offline`、`--timeout`。`search` 另有 `--limit`（1..50）、`--offset`；`fetch` 另有 `--text-out`、`--pdf-out`、`--max-mb`。

## 结果边界

- 站内搜索返回的是官网页面（案件页、新闻稿、公开遗产页面），不是判例全文数据库；`total` 是当前结果页的条目数，不是全站命中总数。
- 判例全文、书状和法庭文件请优先用 `LegalToolsSearcher` 检索 Legal Tools 的 ICTY 馆藏；本 skill 负责官方站点的案件页、新闻稿和页面级材料。
- `fetch` 的 PDF 页号是 PDF 位置，不是印刷页码；扫描件可能 `needs_ocr=true`。
- 新闻稿不是裁判文书；引用案件结论时回到判决/裁定原文，不要把新闻稿当判决理由。

## 参考

- 2026-11-09 实测：`search-results?as_q=`、20 条/页、案件页选择器：[references/icty-search.md](references/icty-search.md)
- 部署、环境与排错：[README.md](README.md)
