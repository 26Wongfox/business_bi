# 平台与工具资源总览（已确认）

状态：`DONE`  
版本：`v02`  
适用：5人兼职团队、多账号运营

## 1) 内容平台基础信息（当前范围：7个平台）
| 平台 | 主要内容形态 | 推荐账号目标 | 关键指标 | 官方入口 |
|---|---|---|---|---|
| 公众号 | 长文/深度解读 | 品牌沉淀与私域承接 | 阅读、在看、分享、关注转化 | https://mp.weixin.qq.com |
| 小红书 | 图文/短视频 | 搜索流量与种草转化 | 点击率、互动率、收藏率 | https://www.xiaohongshu.com |
| 抖音 | 短视频 | 扩散增长与线索获取 | 完播率、互动率、转化率 | https://www.douyin.com |
| 视频号 | 短视频/直播 | 微信生态联动 | 完播率、转粉率、私域转化 | https://channels.weixin.qq.com |
| B站 | 中长视频 | 专业内容与口碑 | 完播率、三连率、关注转化 | https://www.bilibili.com |
| 知乎 | 问答/文章 | 专业信任与搜索长尾 | 阅读、赞同、收藏、私信 | https://www.zhihu.com |
| 微博 | 短帖/热点追踪 | 热点承接与曝光 | 阅读、转评赞、涨粉 | https://weibo.com |

## 2) 工具栈（按角色 A/B 两套）

### A 套（效率优先，推荐默认）
| 角色 | 主工具 | 备用工具 | 费用级别 | 团队版成本(估) | 替代工具 | 风险等级 | 备注 |
|---|---|---|---|---|---|---|---|
| 主编/策略（李然） | 飞书文档 + ChatGPT + Perplexity | Notion + Claude | 中 | 中 | Gemini | 中 | 速度和一致性最佳 |
| 内容生产（王青） | ChatGPT + 飞书 + Notion | Claude | 中 | 中 | 通义/豆包 | 中 | 适合多平台改写 |
| 设计剪辑（陈墨） | Canva + 剪映 | CapCut | 中 | 低-中 | Figma/PS | 中 | 模板化效率高 |
| 运营分发（赵宁） | 飞书 + 平台官方后台 | Notion Calendar | 低-中 | 低 | Buffer(海外) | 低 | 国内平台兼容好 |
| 数据增长（孙越） | 飞书多维表 + Looker Studio | Airtable | 低-中 | 低 | Tableau Public | 中 | 统计口径统一优先 |

### B 套（能力增强，预算充足时）
| 角色 | 主工具 | 备用工具 | 费用级别 | 团队版成本(估) | 替代工具 | 风险等级 | 备注 |
|---|---|---|---|---|---|---|---|
| 主编/策略（李然） | Notion + Claude + Perplexity Pro | ChatGPT Team | 中-高 | 中-高 | 飞书 | 中 | 长文推理更强 |
| 内容生产（王青） | Claude + ChatGPT 双模型 | Gemini | 中-高 | 中-高 | Kimi | 中 | 双模交叉降低幻觉 |
| 设计剪辑（陈墨） | Canva Pro + CapCut Pro | 剪映专业版 | 中-高 | 中 | Figma | 中 | 多端素材协作更顺 |
| 运营分发（赵宁） | 飞书 + 自动化（n8n/Make） | Zapier | 中 | 中 | 手工排程 | 中 | 自动化维护成本上升 |
| 数据增长（孙越） | Airtable + Looker Studio + n8n | 飞书多维表 | 中 | 中 | Metabase | 中 | 结构化分析更强 |

## 3) 通用工具清单（采购与对比字段）
| 类别 | 工具 | 官方网站 | 费用类型(免费/订阅) | 团队版成本(估) | 替代工具 | 风险等级(低/中/高) |
|---|---|---|---|---|---|---|
| 协作 | 飞书 | https://www.feishu.cn | 免费+订阅 | 中 | Notion | 低 |
| 知识库 | Notion | https://www.notion.so | 免费+订阅 | 中 | 飞书文档 | 低 |
| AI生成 | ChatGPT | https://chatgpt.com | 订阅 | 中 | Claude/Gemini | 中 |
| AI生成 | Claude | https://claude.ai | 订阅 | 中 | ChatGPT | 中 |
| AI检索 | Perplexity | https://www.perplexity.ai | 免费+订阅 | 低-中 | Google/Google Scholar | 低 |
| 设计 | Canva | https://www.canva.com | 免费+订阅 | 低-中 | Figma | 低 |
| 剪辑 | 剪映 | https://www.capcut.cn | 免费+订阅 | 低 | CapCut | 低 |
| 自动化 | n8n | https://n8n.io | 开源+托管订阅 | 低-中 | Make | 中 |
| 自动化 | Make | https://www.make.com | 订阅 | 中 | n8n/Zapier | 中 |
| 自动化 | Zapier | https://zapier.com | 订阅 | 中-高 | n8n/Make | 中 |
| 报表 | Looker Studio | https://lookerstudio.google.com | 免费 | 低 | Airtable/Metabase | 低 |

## 4) 与当前项目结构的对应位置
- 平台策略文档：`D_能力与知识资产/10_内容创作者手册/03_平台算法指南/平台算法指南_V1.md`
- 数据源台账：`B_内容生产主流程/02_素材/数据与引用/数据源台账_v01.csv`
- 自动化模板：`D_能力与知识资产/07_模板与自动化/automation/字段与规则/`
- 账号执行看板：`B_内容生产主流程/04_发布/排期看板/DOING_04_ACC-ALL_统一内容看板_2026-02-12_v01.csv`

## 5) 已确认决策
1. 平台范围：暂不扩展，维持当前7个平台。
2. 工具栈：采用按角色 A/B 两套。
3. 采购字段：增加费用、团队版成本、替代工具、风险等级。
