# ICTYSearcher 部署指引

独立检索 ICTY 官网的案件页、新闻稿和公开遗产页面。只访问 `icty.org`。

仓库：<https://github.com/HuiwowICCSkills/ICTYSearcher>（私有）。

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
