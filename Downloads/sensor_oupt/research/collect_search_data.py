#!/usr/bin/env python3
import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import requests

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": UA})
TIMEOUT = 8

ZH_SEEDS = [
    ("WHO", "宝妈在家带娃 谁"),
    ("WHO", "打工人下班后 谁"),
    ("WHO", "自媒体新手没粉丝 谁"),
    ("WHEN", "大学生课多又忙 什么时候"),
    ("WHEN", "上班族晚上做副业 几点"),
    ("WHEN", "新号刚起步 前几天"),
    ("WHERE", "县城做副业 去哪找客户"),
    ("WHERE", "AI模板做好了 发到哪里"),
    ("WHERE", "做中英文市场 在哪个平台"),
    ("WHAT", "会剪视频 做什么副业"),
    ("WHAT", "会写文案 做什么副业"),
    ("WHAT", "Excel不错 能做什么"),
    ("WHY", "小红书有浏览没成交 为什么"),
    ("WHY", "工具做出来卖不动 为什么"),
    ("WHY", "接单收入不稳定 为什么"),
    ("HOW", "不会编程 怎么做AI副业"),
    ("HOW", "宝妈每天1小时 怎么做副业"),
    ("HOW", "设计师不想卖时间 怎么办"),
    ("HOW", "英语一般 怎么做海外副业"),
    ("HOW", "一个人零预算 怎么开始"),
]

EN_SEEDS = [
    ("WHO", "busy moms at home who"),
    ("WHO", "after-work employees who need"),
    ("WHEN", "best time to post side hustle content"),
    ("WHEN", "when to launch an ai tool"),
    ("WHERE", "where to find first side hustle clients"),
    ("WHERE", "where to sell ai templates"),
    ("WHAT", "what ai micro tool can I sell"),
    ("WHY", "why side hustle content gets views no sales"),
    ("HOW", "how to build ai side hustle without coding"),
    ("HOW", "how to get first client with zero budget"),
]

Q_WORDS_ZH = ["怎么", "如何", "为什么", "为何", "哪里", "在哪", "谁", "什么时候", "咋", "怎么办", "吗"]
Q_WORDS_EN = ["how", "why", "where", "who", "when", "what", "should", "can", "is ", "are "]


def baidu_autocomplete(query: str):
    url = f"https://www.baidu.com/sugrec?prod=pc&wd={quote(query)}"
    try:
        r = SESSION.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return []
    out = []
    for item in data.get("g", []):
        q = item.get("q")
        if q:
            out.append(q.strip())
    return out


def google_autocomplete(query: str, hl: str):
    url = f"https://suggestqueries.google.com/complete/search?client=chrome&hl={hl}&q={quote(query)}"
    try:
        r = SESSION.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        arr = r.json()
    except Exception:
        return []
    if isinstance(arr, list) and len(arr) > 1 and isinstance(arr[1], list):
        return [str(x).strip() for x in arr[1] if str(x).strip()]
    return []


def google_gws_related(query: str, hl: str):
    url = f"https://www.google.com/complete/search?client=gws-wiz&hl={hl}&q={quote(query)}"
    try:
        r = SESSION.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        txt = r.text
    except Exception:
        return []
    # format like: window.google.ac.h([[['xxx',0,[...]], ...], {...}])
    m = re.search(r"window\.google\.ac\.h\((.*)\)\s*$", txt)
    if not m:
        return []
    payload = m.group(1)
    payload = payload.replace("'", '"')
    payload = re.sub(r",\s*([}\]])", r"\1", payload)
    try:
        obj = json.loads(payload)
    except Exception:
        return []
    out = []
    if isinstance(obj, list) and obj:
        first = obj[0]
        if isinstance(first, list):
            for item in first:
                if isinstance(item, list) and item:
                    s = str(item[0]).strip()
                    if s:
                        out.append(s)
    return out


def is_question_like(text: str, lang: str):
    t = text.strip().lower()
    if "?" in t or "？" in t:
        return True
    if lang == "zh":
        return any(w in t for w in Q_WORDS_ZH)
    return any(t.startswith(w) or f" {w}" in t for w in Q_WORDS_EN)


def dedupe_keep_order(items):
    seen = set()
    out = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out


def collect_for_seed(seed_id, w_type, seed_query, lang):
    rows = []

    # level-1 autocomplete
    baidu_l1 = baidu_autocomplete(seed_query) if lang == "zh" else []
    google_l1 = google_autocomplete(seed_query, "zh-CN" if lang == "zh" else "en")
    google_rel = google_gws_related(seed_query, "zh-CN" if lang == "zh" else "en")

    for i, s in enumerate(baidu_l1, 1):
        rows.append((seed_id, lang, w_type, seed_query, "baidu", "autocomplete", i, s))
    for i, s in enumerate(google_l1, 1):
        rows.append((seed_id, lang, w_type, seed_query, "google", "autocomplete", i, s))
    for i, s in enumerate(google_rel, 1):
        rows.append((seed_id, lang, w_type, seed_query, "google", "related_search", i, s))

    # level-2 expansion as related search proxy
    for engine, l1 in (("baidu", baidu_l1), ("google", google_l1)):
        top = l1[:2]
        for base in top:
            if engine == "baidu":
                l2 = baidu_autocomplete(base) if lang == "zh" else []
            else:
                l2 = google_autocomplete(base, "zh-CN" if lang == "zh" else "en")
            l2 = dedupe_keep_order([x for x in l2 if x != base and x != seed_query])[:5]
            for j, s in enumerate(l2, 1):
                rows.append((seed_id, lang, w_type, seed_query, engine, "related_search", j, s))

    # derive PAA-like question set from collected suggestions (engine-grounded)
    grouped = []
    for _, _, _, _, eng, _, _, text in rows:
        grouped.append((eng, text))
    by_engine = {"baidu": [], "google": []}
    for eng, txt in grouped:
        if is_question_like(txt, lang):
            by_engine[eng].append(txt)
    for eng in by_engine:
        qset = dedupe_keep_order(by_engine[eng])[:10]
        for i, s in enumerate(qset, 1):
            rows.append((seed_id, lang, w_type, seed_query, eng, "people_also_ask", i, s))

    # final dedupe by unique tuple
    uniq = []
    seen = set()
    for row in rows:
        k = row
        if k not in seen:
            seen.add(k)
            uniq.append(row)
    return uniq


def load_seeds_from_csv(path: Path):
    out = []
    with path.open("r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            lang = (r.get("lang") or "").strip().lower()
            w_type = (r.get("w_type") or "").strip().upper()
            q = (r.get("query_prefix") or "").strip()
            if lang in {"zh", "en"} and w_type and q:
                out.append((lang, w_type, q))
    return out


def main():
    parser = argparse.ArgumentParser(description="Collect search suggestion signals from Baidu and Google.")
    parser.add_argument("--seed-file", help="CSV with columns: lang,w_type,query_prefix", default="")
    args = parser.parse_args()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("data") / f"search_research_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    seed_meta = []

    if args.seed_file:
        seed_file = Path(args.seed_file)
        external = load_seeds_from_csv(seed_file)
        zh_i = 1
        en_i = 1
        for lang, w_type, q in external:
            if lang == "zh":
                sid = f"ZH{zh_i:02d}"
                zh_i += 1
            else:
                sid = f"EN{en_i:02d}"
                en_i += 1
            seed_meta.append((sid, lang, w_type, q))
            rows.extend(collect_for_seed(sid, w_type, q, lang))
    else:
        idx = 1
        for w_type, q in ZH_SEEDS:
            sid = f"ZH{idx:02d}"
            seed_meta.append((sid, "zh", w_type, q))
            rows.extend(collect_for_seed(sid, w_type, q, "zh"))
            idx += 1

        idx = 1
        for w_type, q in EN_SEEDS:
            sid = f"EN{idx:02d}"
            seed_meta.append((sid, "en", w_type, q))
            rows.extend(collect_for_seed(sid, w_type, q, "en"))
            idx += 1

    seed_path = out_dir / "seed_queries.csv"
    with seed_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["seed_id", "lang", "w_type", "query_prefix"])
        w.writerows(seed_meta)

    data_path = out_dir / "search_signals.csv"
    with data_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "seed_id",
            "lang",
            "w_type",
            "seed_query",
            "engine",
            "signal_type",
            "rank",
            "text",
        ])
        w.writerows(rows)

    # quick metrics
    metrics = {
        "generated_at": ts,
        "seed_count": len(seed_meta),
        "signal_count": len(rows),
    }
    m_path = out_dir / "metrics.json"
    m_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    print(out_dir)
    print(json.dumps(metrics, ensure_ascii=False))


if __name__ == "__main__":
    main()
