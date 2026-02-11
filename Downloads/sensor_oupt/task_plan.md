# Task Plan: 搜索联想需求采集与AI副业机会探索

## Goal
基于20条5W1H口语化前缀查询词，采集百度+Google自动补全及扩展问题数据，落盘后输出一份Markdown副业机会探索报告（工具型优先）。

## Phases
- [x] Phase 1: Plan and setup
- [x] Phase 2: Data collection (autocomplete + related + PAA proxy)
- [x] Phase 3: Analysis and opportunity mining
- [x] Phase 4: Review and deliver

## Key Questions
1. 在当前环境下，百度与Google哪些接口可稳定返回“联想句”数据？
2. “相关搜索/大家还在问”在反爬限制下如何可复现采集？
3. 如何将需求信号映射为低成本AI副业方向（工具型>内容型>服务型）？

## Decisions Made
- 使用 `planning-with-files` 三文件模式执行本次多步骤任务。
- 查询输入采用“人群+场景+5W1H关键词”的不完整前缀，而非完整句子。
- 数据源固定为百度+Google，中文优先，并补充英文镜像探索。
- 相关搜索/PAA在当前环境采用“二跳联想扩展 + 问句过滤”的可复现代理实现。

## Errors Encountered
- `python-docx` 不可用（前序任务）: 已改用纯文本/RTF输出（与本任务无直接冲突）。
- 直接抓取百度/Google SERP触发反爬或动态壳页面: 改为使用可稳定的建议接口 + 二跳扩展近似相关/问题。
- 首轮采集脚本因超时策略过重运行过慢: 已将请求改为 Session + 8s超时 + 失败自动跳过 + 二跳减量。

## Status
**Completed** - 数据采集、分析与Markdown报告均已输出。
