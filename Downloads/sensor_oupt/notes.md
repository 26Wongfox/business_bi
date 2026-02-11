# Notes: 搜索联想采集与副业探索

## Sources

### Source 1: 百度建议接口
- Endpoint: `https://www.baidu.com/sugrec?prod=pc&wd={query}`
- Key points:
  - 可稳定返回 JSON，包含建议词数组 `g[].q`
  - 适合采集“自动补全联想句”

### Source 2: Google Suggest
- Endpoint: `https://suggestqueries.google.com/complete/search?client=chrome&hl={hl}&q={query}`
- Key points:
  - 可返回建议词数组（第2项）
  - 中文返回相对稀疏，但英文更丰富

### Source 3: Google complete (gws-wiz)
- Endpoint: `https://www.google.com/complete/search?client=gws-wiz&hl={hl}&q={query}`
- Key points:
  - 返回 JS 包装数据，包含备选查询
  - 可作为 related 扩展来源

## Synthesized Findings

### 数据可用性
- 自动补全：百度、Google均可用。
- 相关搜索/PAA：直接SERP抓取稳定性差，采用“二跳建议扩展 + 问句过滤”作为可复现替代。

### 本次落地结果
- 数据目录：`data/search_research_20260211_180307`
- 原始信号：`search_signals.csv`，共 1018 条
- 种子查询：`seed_queries.csv`，共 30 条（中文20+英文10）
- 报告文件：`reports/ai_side_hustle_exploration_20260211_180405.md`
