import json
import duckdb
from pathlib import Path
from common import load_config

cfg = load_config()
db_path = Path(cfg["outputs"]["duckdb_path"])
con = duckdb.connect(str(db_path))

# Core metrics
metrics = {}
metrics["sales_post_total"] = con.execute("SELECT SUM(sales_amount_post) FROM fact_sales").fetchone()[0] or 0
metrics["specimen_total"] = con.execute("SELECT SUM(specimen_qty) FROM fact_sales").fetchone()[0] or 0
metrics["forecast_3m"] = con.execute("SELECT forecast_amount FROM forecast_3m").fetchone()[0] or 0
metrics["unpaid_total"] = con.execute("SELECT SUM(unpaid_amount) FROM fact_payment").fetchone()[0] or 0

# Trends
sales_monthly = con.execute("""
    SELECT CAST(month AS VARCHAR) AS month, SUM(sales_amount_post) AS value
    FROM sales_monthly
    GROUP BY 1
    ORDER BY 1
""").fetchall()

# Top hospitals/items
top_hospitals = con.execute("SELECT hospital_name, sales_amount_post FROM top_hospitals").fetchall()
top_items = con.execute("SELECT marketing_package, sales_amount_post FROM top_items").fetchall()

# Aging buckets
aging = con.execute("SELECT aging_bucket, unpaid_amount FROM ar_aging").fetchall()

# DSO outliers
risk_dso = con.execute("""
    SELECT hospital_name, dso_days
    FROM dso
    WHERE dso_days IS NOT NULL
    ORDER BY dso_days DESC
    LIMIT 10
""").fetchall()

# Tier-3 hospitals trend
tier3_trend = con.execute("""
    SELECT CAST(month AS VARCHAR) AS month, SUM(sales_amount_post) AS value
    FROM sales_monthly sm
    JOIN dim_hospital h
      ON sm.hospital_code = h.hospital_code
    WHERE h.hospital_level LIKE '%三%'
    GROUP BY 1
    ORDER BY 1
""").fetchall()

# Opportunity leads
leads = con.execute("""
    SELECT source_file, regions, diseases, policies, opportunity_score, suggested_action
    FROM opportunity_leads
    ORDER BY opportunity_score DESC
    LIMIT 20
""").fetchall()

lead_score = con.execute("""
    SELECT opportunity_score AS score, COUNT(*) AS cnt
    FROM opportunity_leads
    GROUP BY 1
    ORDER BY 1
""").fetchall()

con.close()

out = {
    "metrics": metrics,
    "sales_monthly": [{"month": m, "value": float(v or 0)} for m, v in sales_monthly],
    "top_hospitals": [{"name": n, "value": float(v or 0)} for n, v in top_hospitals],
    "top_items": [{"name": n, "value": float(v or 0)} for n, v in top_items],
    "aging": [{"bucket": b, "value": float(v or 0)} for b, v in aging],
    "risk_dso": [{"name": n, "value": float(v or 0)} for n, v in risk_dso],
    "tier3_trend": [{"month": m, "value": float(v or 0)} for m, v in tier3_trend],
    "leads": [
        {
            "source_file": r,
            "regions": reg,
            "diseases": dis,
            "policies": pol,
            "score": float(score or 0),
            "action": action,
        }
        for r, reg, dis, pol, score, action in leads
    ],
    "lead_score": [{"score": float(s), "count": int(c)} for s, c in lead_score],
}

out_path = Path(__file__).resolve().parents[1] / "output" / "demo_data.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
with out_path.open("w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f"Demo JSON written: {out_path}")
