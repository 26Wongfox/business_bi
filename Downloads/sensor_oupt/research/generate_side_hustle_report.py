#!/usr/bin/env python3
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

THEME_RULES = [
    ("变现与赚钱", [r"赚钱", r"变现", r"收入", r"副业", r"下单", r"客户", r"盈利", r"make money", r"monetiz", r"client"]),
    ("起步与方法", [r"怎么", r"如何", r"怎么办", r"开始", r"起步", r"流程", r"how to", r"start"]),
    ("流量与增长", [r"流量", r"浏览", r"粉丝", r"曝光", r"起号", r"发布", r"增长", r"views", r"growth"]),
    ("平台与渠道", [r"哪里", r"在哪", r"平台", r"渠道", r"去哪", r"where", r"platform"]),
    ("时间与效率", [r"时间", r"下班", r"晚上", r"1小时", r"自动", r"提效", r"效率", r"time", r"efficient"]),
    ("技能产品化", [r"模板", r"工具", r"excel", r"剪辑", r"文案", r"设计", r"product", r"template", r"tool"]),
    ("跨境与英文", [r"英文", r"英语", r"海外", r"global", r"english", r"overseas"]),
]

OPPORTUNITY_PLAYBOOK = [
    {
        "name": "AI简历与求职材料生成微工具",
        "fit": "起步与方法 + 变现与赚钱",
        "target": "转行/求职人群、在家待业人群",
        "solution": "输入岗位JD，自动生成简历版本、求职信、面试问答清单",
        "stack": "Notion + 表单 + OpenAI API/通义 + Cloudflare Workers",
        "cost": "低（可先无代码）",
        "pricing": "9.9-39元/次 或 99元/月",
        "mvp": "Day1-2做模板；Day3接API；Day4发布；Day5-7收首批反馈",
        "type_priority": 3,
    },
    {
        "name": "AI爆款选题与脚本助手（短视频/图文）",
        "fit": "流量与增长 + 时间与效率",
        "target": "自媒体新手、兼职创作者",
        "solution": "输入账号定位，输出选题库、标题、脚本、封面文案",
        "stack": "飞书多维表格 + 自动化机器人 + 大模型",
        "cost": "低",
        "pricing": "订阅制 29-199元/月",
        "mvp": "先做手工代跑服务，验证后再工具化",
        "type_priority": 3,
    },
    {
        "name": "AI接单报价与需求澄清机器人",
        "fit": "变现与赚钱 + 平台与渠道",
        "target": "设计/文案/剪辑自由职业者",
        "solution": "自动把模糊需求转成报价单、交付清单、里程碑",
        "stack": "网页表单 + LLM + PDF导出",
        "cost": "低",
        "pricing": "19元/次 或 199元年费",
        "mvp": "聚焦单一职业（如剪辑）先做垂直版本",
        "type_priority": 3,
    },
    {
        "name": "AI模板小店（Excel/提示词/工作流）",
        "fit": "技能产品化 + 变现与赚钱",
        "target": "有基础办公技能的上班族",
        "solution": "销售可复用模板包，附AI使用说明",
        "stack": "公众号/知识星球/小报童 + 网盘交付",
        "cost": "极低",
        "pricing": "19-299元/包",
        "mvp": "先上架3个细分模板，观察复购",
        "type_priority": 3,
    },
    {
        "name": "双语内容本地化AI助手",
        "fit": "跨境与英文 + 流量与增长",
        "target": "想做中英双平台的个人创作者",
        "solution": "中文内容一键转英文并做平台风格重写",
        "stack": "LLM + 术语库 + 发布清单",
        "cost": "低",
        "pricing": "49元/月起",
        "mvp": "从单一领域（效率工具）开始",
        "type_priority": 2,
    },
    {
        "name": "AI副业诊断咨询（轻服务）",
        "fit": "起步与方法 + 变现与赚钱",
        "target": "零经验但有副业意愿人群",
        "solution": "用采集到的问题库做个性化路线图",
        "stack": "问卷 + 诊断模板 + LLM",
        "cost": "低",
        "pricing": "99-499元/次",
        "mvp": "每周固定时段接5位，沉淀为后续工具需求",
        "type_priority": 1,
    },
]


def load_latest_data():
    base = Path("data")
    dirs = sorted([p for p in base.glob("search_research_*") if p.is_dir()])
    if not dirs:
        raise FileNotFoundError("No data/search_research_* directory found")
    latest = dirs[-1]
    signals = latest / "search_signals.csv"
    seeds = latest / "seed_queries.csv"
    if not signals.exists() or not seeds.exists():
        raise FileNotFoundError("Required CSV files missing in latest dataset")
    return latest, seeds, signals


def read_csv(path):
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def match_themes(text):
    t = text.lower()
    matched = []
    for name, patterns in THEME_RULES:
        for p in patterns:
            if re.search(p, t):
                matched.append(name)
                break
    if not matched:
        matched = ["其他"]
    return matched


def top_samples(rows, k=8):
    seen = set()
    out = []
    for r in rows:
        txt = r["text"].strip()
        if txt and txt not in seen:
            seen.add(txt)
            out.append(txt)
        if len(out) >= k:
            break
    return out


def main():
    dataset_dir, seeds_path, signals_path = load_latest_data()
    seeds = read_csv(seeds_path)
    rows = read_csv(signals_path)

    by_lang = Counter(r["lang"] for r in rows)
    by_engine = Counter(r["engine"] for r in rows)
    by_type = Counter(r["signal_type"] for r in rows)

    theme_counter = Counter()
    theme_examples = defaultdict(list)
    for r in rows:
        txt = r["text"]
        for th in match_themes(txt):
            theme_counter[th] += 1
            if len(theme_examples[th]) < 6:
                theme_examples[th].append(txt)

    top_themes = theme_counter.most_common(6)

    # Score opportunities by theme coverage + type priority (工具型高)
    score_map = {name: score for name, score in top_themes}
    scored_ops = []
    for op in OPPORTUNITY_PLAYBOOK:
        fit_parts = [x.strip() for x in op["fit"].split("+")]
        demand_score = sum(score_map.get(x, 0) for x in fit_parts)
        total = demand_score * 10 + op["type_priority"] * 20
        item = dict(op)
        item["demand_score"] = demand_score
        item["total_score"] = total
        scored_ops.append(item)
    scored_ops.sort(key=lambda x: x["total_score"], reverse=True)

    report_dir = Path("reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"ai_side_hustle_exploration_{ts}.md"

    with report_path.open("w", encoding="utf-8") as f:
        f.write("# 用户需求采集与AI副业机会探索报告\n\n")
        f.write("## 1. 调研范围与方法\n")
        f.write("- 数据来源：百度、Google\n")
        f.write("- 查询方式：5W1H口语化前缀（不完整句子）\n")
        f.write("- 采集信号：自动补全（autocomplete）+ 相关搜索扩展（related_search）+ 大家还在问代理（people_also_ask）\n")
        f.write(f"- 种子数量：{len(seeds)}（中文20 + 英文10）\n")
        f.write(f"- 数据集路径：`{dataset_dir}`\n\n")

        f.write("## 2. 采集结果概览\n")
        f.write(f"- 信号总量：**{len(rows)}**\n")
        f.write(f"- 按语言：{dict(by_lang)}\n")
        f.write(f"- 按引擎：{dict(by_engine)}\n")
        f.write(f"- 按信号类型：{dict(by_type)}\n\n")

        f.write("## 3. 高频需求主题（来自搜索联想）\n")
        f.write("| 主题 | 命中数 | 代表联想句（示例） |\n")
        f.write("|---|---:|---|\n")
        for th, cnt in top_themes:
            ex = "；".join(theme_examples[th][:3])
            f.write(f"| {th} | {cnt} | {ex} |\n")
        f.write("\n")

        f.write("## 4. 副业机会清单（工具型 > 内容型 > 服务型）\n")
        f.write("| 优先级 | 方向 | 类型 | 目标用户 | AI方案 | 变现方式 | 启动成本 | 7天MVP |\n")
        f.write("|---:|---|---|---|---|---|---|---|\n")
        for i, op in enumerate(scored_ops[:6], 1):
            t = "工具型" if op["type_priority"] == 3 else ("内容型" if op["type_priority"] == 2 else "服务型")
            f.write(
                f"| {i} | {op['name']} | {t} | {op['target']} | {op['solution']} | {op['pricing']} | {op['cost']} | {op['mvp']} |\n"
            )
        f.write("\n")

        f.write("## 5. 可立即执行的前三个方向\n")
        for i, op in enumerate(scored_ops[:3], 1):
            f.write(f"### {i}. {op['name']}\n")
            f.write(f"- 为什么现在做：命中主题 `{op['fit']}`，需求信号高。\n")
            f.write(f"- 最小可行版本：{op['mvp']}\n")
            f.write(f"- 技术栈建议：{op['stack']}\n")
            f.write(f"- 定价起点：{op['pricing']}\n\n")

        f.write("## 6. 风险与说明\n")
        f.write("- 由于搜索引擎反爬限制，‘相关搜索/PAA’采用可复现的二跳联想扩展与问句过滤实现。\n")
        f.write("- 建议后续用浏览器自动化补采SERP真实模块，做二次校验。\n")

    # dump short machine summary
    summary = {
        "dataset": str(dataset_dir),
        "report": str(report_path),
        "signals": len(rows),
        "top_themes": top_themes,
        "top_opportunities": [x["name"] for x in scored_ops[:3]],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
