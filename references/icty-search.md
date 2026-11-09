# ICTY 检索实测记录（2026-11-09）

## 站内搜索

`https://www.icty.org/en/search-results?as_q=<query>&page=<0-based>`

- 结果选择器：`.search-results h3 a` 或 `.search-result h3 a`
- 实测 `Karadzic` → 20 条；第一条 `Karadžić (IT-95-5/18)` → `/en/case/karadzic`
- 结果混合案件页、新闻稿和其他公开页面

## 页面正文

`https://www.icty.org/en/case/karadzic` → `article` 文本 2,208 字符；不要用空的 `#main-content`。

## 边界

- 站内搜索不是判例全文数据库；`total` 只是当前结果页条目数。
- 判例、书状和法庭文件优先用 `LegalToolsSearcher`。
