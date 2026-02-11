# Score Rules (海外数据可视化内容生产 2.0)

评分总分：100 分。

- `demand_score`（需求强度，0-25）
- `localization_score`（本地化空间，0-20）
- `cost_score`（二次创作成本，0-20，分越高代表成本越低）
- `distribution_score`（分发潜力，0-15）
- `monetization_score`（变现潜力，0-15）
- `copyright_risk`（版权风险扣分，0-5）

计算公式：

```text
final_score = demand_score + localization_score + cost_score + distribution_score + monetization_score - copyright_risk
```

分层规则：

- `production_pool`：`final_score >= 70`
- `observation_pool`：`50 <= final_score <= 69`
- `archive_pool`：`final_score < 50`

建议流程：

1. 每日批量入库候选主题。
2. 脚本自动初评后，人工复核前 20 条。
3. 从 `production_pool` 选择 3 条进入当天创作。
4. 发布后回填效果数据（曝光、收藏、转化），用于下轮调权。
