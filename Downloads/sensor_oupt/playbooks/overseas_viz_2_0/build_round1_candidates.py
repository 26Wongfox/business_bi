#!/usr/bin/env python3
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

INPUT = Path("data/search_research_20260211_195604/search_signals.csv")
OUT_CSV = Path("playbooks/overseas_viz_2_0/topic_pipeline_round1_20260211.csv")
OUT_MD = Path("reports/round4_assets/overseas_viz_topic_pool_round1_2026-02-11.md")

KEYWORDS = {
    "模板定价与成交优化助手": ["模板", "定价", "报价", "成交", "拒绝", "卖多少钱", "价格"],
    "同城首单获客路径生成器": ["同城", "首单", "获客", "small town", "first paying client", "渠道"],
    "有流量没成交诊断器": ["流量", "不回复", "没回复", "已读不回", "转化", "文案"],
}

HIGH_INTENT = [
    "多少钱", "报价", "成交", "怎么", "怎么办", "why", "how", "client", "paying", "转化", "付费",
]

LOW_COST = ["模板", "文案", "话术", "清单", "脚本", "prompt", "sop"]
HIGH_RISK = ["搬运", "原图", "转载", "盗图", "copy"]
SIDE_HUSTLE_INTENT = [
    "副业", "ai", "接单", "客户", "报价", "成交", "获客", "流量", "变现", "模板包", "文案", "同城",
    "首单", "不回复", "赚钱", "paying client", "small town", "local client", "offer",
]
NOISE_PATTERNS = [
    "包工包料", "一平方", "模板一块", "钢模板", "建筑模板", "工地", "木工", "施工", "装修模板",
]

def contains_any(text: str, patterns):
    t = text.lower()
    return any(p.lower() in t for p in patterns)

def infer_topic(text: str):
    best_topic = "通用副业执行"
    best_hits = 0
    for topic, words in KEYWORDS.items():
        hits = sum(1 for w in words if w.lower() in text.lower())
        if hits > best_hits:
            best_hits = hits
            best_topic = topic
    return best_topic

def score_row(text: str, lang: str, signal_type: str):
    demand = 10 + (8 if contains_any(text, HIGH_INTENT) else 0) + (3 if signal_type in {"related_search", "people_also_ask"} else 0)
    demand = min(demand, 25)

    localization = 12
    if contains_any(text, ["同城", "小镇", "local", "small town", "township"]):
        localization += 6
    elif lang == "zh":
        localization += 4
    localization = min(localization, 20)

    cost = 12 + (6 if contains_any(text, LOW_COST) else 0)
    cost = min(cost, 20)

    distribution = 8
    if contains_any(text, ["模板", "清单", "步骤", "脚本", "案例"]):
        distribution += 4
    if contains_any(text, ["同城", "首单", "不回复"]):
        distribution += 2
    distribution = min(distribution, 15)

    monetization = 8
    if contains_any(text, ["报价", "定价", "成交", "付费", "赚钱", "卖"]):
        monetization += 6
    if contains_any(text, ["模板"]):
        monetization += 1
    monetization = min(monetization, 15)

    risk = 1 + (2 if contains_any(text, HIGH_RISK) else 0)
    risk = min(risk, 5)

    final_score = demand + localization + cost + distribution + monetization - risk
    if final_score >= 70:
        tier = "production_pool"
    elif final_score >= 50:
        tier = "observation_pool"
    else:
        tier = "archive_pool"

    return demand, localization, cost, distribution, monetization, risk, final_score, tier


def main():
    rows = []
    seen = set()
    with INPUT.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            text = (r.get("text") or "").strip()
            if not text or text in seen:
                continue
            if not contains_any(text, SIDE_HUSTLE_INTENT):
                continue
            if contains_any(text, NOISE_PATTERNS):
                continue
            seen.add(text)
            demand, localization, cost, distribution, monetization, risk, final_score, tier = score_row(
                text=text,
                lang=(r.get("lang") or "zh"),
                signal_type=(r.get("signal_type") or "autocomplete"),
            )
            rows.append({
                "source_url": f"https://search.example/{r.get('engine','unknown')}",
                "title": text,
                "publish_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "topic": infer_topic(text),
                "chart_type": "bar",
                "tool": "Canva",
                "region": "CN" if (r.get("lang") == "zh") else "Global",
                "language": r.get("lang") or "zh",
                "demand_score": demand,
                "localization_score": localization,
                "cost_score": cost,
                "distribution_score": distribution,
                "monetization_score": monetization,
                "copyright_risk": risk,
                "final_score": final_score,
                "pool_tier": tier,
                "signal_type": r.get("signal_type"),
                "engine": r.get("engine"),
            })

    rows.sort(key=lambda x: x["final_score"], reverse=True)

    # Keep topic diversity to avoid one-topic domination.
    quota = {
        "模板定价与成交优化助手": 8,
        "同城首单获客路径生成器": 6,
        "有流量没成交诊断器": 6,
    }
    top20 = []
    for topic, cap in quota.items():
        picked = [r for r in rows if r["topic"] == topic][:cap]
        top20.extend(picked)
    if len(top20) < 20:
        picked_titles = {r["title"] for r in top20}
        for r in rows:
            if r["title"] in picked_titles:
                continue
            top20.append(r)
            if len(top20) == 20:
                break

    counts = defaultdict(int)
    for r in top20:
        counts[r["topic"]] += 1

    fieldnames = [
        "topic_id", "source_url", "title", "publish_time", "topic", "chart_type", "tool", "region", "language",
        "demand_score", "localization_score", "cost_score", "distribution_score", "monetization_score", "copyright_risk",
        "final_score", "pool_tier", "status", "owner", "next_action", "notes"
    ]

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, r in enumerate(top20, 1):
            writer.writerow({
                "topic_id": f"T{i:04d}",
                "source_url": r["source_url"],
                "title": r["title"],
                "publish_time": r["publish_time"],
                "topic": r["topic"],
                "chart_type": r["chart_type"],
                "tool": r["tool"],
                "region": r["region"],
                "language": r["language"],
                "demand_score": r["demand_score"],
                "localization_score": r["localization_score"],
                "cost_score": r["cost_score"],
                "distribution_score": r["distribution_score"],
                "monetization_score": r["monetization_score"],
                "copyright_risk": r["copyright_risk"],
                "final_score": r["final_score"],
                "pool_tier": r["pool_tier"],
                "status": "new",
                "owner": "AI",
                "next_action": "生成为静态+动态双版本初稿",
                "notes": f"engine={r['engine']}; signal_type={r['signal_type']}",
            })

    prod = sum(1 for r in top20 if r["pool_tier"] == "production_pool")
    obs = sum(1 for r in top20 if r["pool_tier"] == "observation_pool")

    with OUT_MD.open("w", encoding="utf-8") as f:
        f.write("# Round4 首轮候选池（20条）\n\n")
        f.write(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"- 数据源：`{INPUT}`\n")
        f.write(f"- 产出表：`{OUT_CSV}`\n\n")

        f.write("## 分层结果\n\n")
        f.write(f"- production_pool: {prod}\n")
        f.write(f"- observation_pool: {obs}\n\n")

        f.write("## 主题分布\n\n")
        for topic, c in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- {topic}: {c}\n")

        f.write("\n## Top 10\n\n")
        f.write("| 排名 | 分数 | 分层 | 主题 | 标题 |\n")
        f.write("|---:|---:|---|---|---|\n")
        for i, r in enumerate(top20[:10], 1):
            f.write(f"| {i} | {r['final_score']} | {r['pool_tier']} | {r['topic']} | {r['title']} |\n")

if __name__ == "__main__":
    main()
