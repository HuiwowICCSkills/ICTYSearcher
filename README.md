# ICTYSearcher 部署指引

独立检索 ICTY 官网的案件页、新闻稿和公开遗产页面。只访问 `icty.org`。

仓库：<https://github.com/HuiwowICCSkills/ICTYSearcher>（公开）。

## 1. 环境

Python 3.10+，依赖 `requests`、`beautifulsoup4`、`pypdf`；无需登录。

## 2. 安装

```powershell
git clone https://github.com/HuiwowICCSkills/ICTYSearcher.git "$env:USERPROFILE\.codex\skills\ICTYSearcher"
python -m pip install -r "$env:USERPROFILE\.codex\skills\ICTYSearcher\requirements.txt"
```

## 3. 自检

```powershell
& "$env:USERPROFILE\.codex\skills\ICTYSearcher\run.ps1" doctor
```

## 4. 使用

```powershell
$icty = "$env:USERPROFILE\.codex\skills\ICTYSearcher\run.ps1"
& $icty search 'Karadzic' --limit 10 --out './icty.json'
& $icty fetch 'https://www.icty.org/en/case/karadzic' --out './case.json' --text-out './case.txt'
```

## 5. 排错

| 现象 | 处理 |
| --- | --- |
| 搜索返回新闻稿多 | 站内搜索覆盖新闻/案件/遗产页面；按 `section` 过滤或改用 LegalTools |
| `Insufficient ICTY page text` | 页面选择器变化；检查 `article`/`main` 结构 |

## 6. 边界

本 skill 不是判例全文数据库；判例、书状和法庭文件优先用 `LegalToolsSearcher`。

## 实测效果（2026-11-09）

以下命令与结果来自本机 `~/.codex/skills/ICTYSearcher` 的实网运行；检索日期 2026-11-09（Asia/Shanghai），输出为该次运行实际返回的 JSON 报告。

```powershell
& .\run.ps1 search 'Karadzic' --limit 5
```

- 状态：`ok`；服务端/索引报告 `total = 20`；本次返回 5 条。
- 代表性结果：

| 题名 | 类型 / 日期 | 链接 |
| --- | --- | --- |
| Karadžić (IT-95-5/18) | retrieved_metadata / case-page；无日期字段 | https://www.icty.org/en/case/karadzic |
| Tribunal convicts Radovan Karadžić for crimes in Bosnia and Herzegovina | retrieved_metadata / press-release；无日期字段 | https://www.icty.org/en/press/tribunal-convicts-radovan-karadzic-for-crimes-in-bosnia-and-herzegovina |
| Milan Martic, Radovan Karadzic and Ratko Mladic indicted along with 21 other accused. | retrieved_metadata / press-release；无日期字段 | https://www.icty.org/en/press/milan-martic-radovan-karadzic-and-ratko-mladic-indicted-along-21-other-accused |

> 说明：`total = 20` 是 ICTY 官网站内搜索对 `Karadzic` 的命中数（`scope`：Official ICTY site search (cases, press releases and legacy pages); not a full-text judgment database）。本轮命中的第一条是案件页 `case-page`，其余 4 条均为新闻稿 `press-release`；JSON 没有日期字段，本表不补写日期。结果行是站点页面元数据（`result_type = retrieved_metadata`，`content_scope`：site search record, not the linked judgment or press release text），只能证明页面被站内检索命中，不能作为判决理由；判决全文与书状须用 `LegalToolsSearcher` 或 `fetch` 取得。