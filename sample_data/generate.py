"""
Generate deterministic sample datasets for MetricAnchor demos.

Usage:
    python sample_data/generate.py

Outputs (in same directory):
    retail_sales.csv       – 520 rows, Jan 2025–Feb 2026
    support_tickets.csv    – 400 rows, Oct 2025–Feb 2026
    saas_funnel.csv        – 300 rows, Jul 2025–Feb 2026
"""

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
OUT = Path(__file__).parent

# ── Helpers ───────────────────────────────────────────────────────────────────

def weighted_choice(rng, options, weights):
    cum = []
    total = 0
    for w in weights:
        total += w
        cum.append(total)
    r = rng.random() * total
    for opt, c in zip(options, cum):
        if r <= c:
            return opt
    return options[-1]


def date_range(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


# ── retail_sales.csv ──────────────────────────────────────────────────────────

def gen_retail_sales(rng: random.Random) -> list[dict]:
    start = date(2025, 1, 1)
    end = date(2026, 2, 28)

    PRODUCTS = ["Electronics", "Apparel", "Home", "Sports", "Beauty"]
    PROD_W = [0.20, 0.25, 0.20, 0.20, 0.15]

    REGIONS = ["North", "South", "East", "West"]
    REGION_W = [0.30, 0.25, 0.25, 0.20]

    CHANNELS = ["Online", "In-Store", "Wholesale"]
    CHANNEL_W = [0.60, 0.30, 0.10]

    # unit revenue range per product, margin rate range
    PROD_CONFIG = {
        "Electronics": {"rev": (50, 400), "margin": (0.16, 0.23)},
        "Apparel":     {"rev": (30, 150), "margin": (0.42, 0.54)},
        "Home":        {"rev": (25, 200), "margin": (0.36, 0.46)},
        "Sports":      {"rev": (20, 180), "margin": (0.30, 0.44)},
        "Beauty":      {"rev": (15,  80), "margin": (0.56, 0.68)},
    }

    rows = []
    # ~520 rows: ~1–2 orders per day, more in Q4
    all_days = list(date_range(start, end))
    for d in all_days:
        # Q4 seasonality: Oct–Dec gets ~2x volume
        n = rng.choices([1, 2, 3], weights=[0.50, 0.35, 0.15])[0]
        if 10 <= d.month <= 12:
            n = rng.choices([1, 2, 3, 4], weights=[0.25, 0.35, 0.25, 0.15])[0]
        for _ in range(n):
            product = weighted_choice(rng, PRODUCTS, PROD_W)
            region = weighted_choice(rng, REGIONS, REGION_W)
            channel = weighted_choice(rng, CHANNELS, CHANNEL_W)
            cfg = PROD_CONFIG[product]

            units = rng.choices([1, 2, 3, 4, 5, 10], weights=[0.45, 0.25, 0.12, 0.08, 0.06, 0.04])[0]
            unit_rev = rng.uniform(*cfg["rev"])
            revenue = round(units * unit_rev, 2)
            margin_rate = rng.uniform(*cfg["margin"])
            cost = round(revenue * (1 - margin_rate), 2)
            margin = round(revenue - cost, 2)

            rows.append({
                "order_date": d.isoformat(),
                "region": region,
                "product": product,
                "channel": channel,
                "units": units,
                "revenue": revenue,
                "cost": cost,
                "margin": margin,
            })
    return rows


# ── support_tickets.csv ───────────────────────────────────────────────────────

def gen_support_tickets(rng: random.Random) -> list[dict]:
    start = date(2025, 10, 1)
    end = date(2026, 2, 28)

    TEAMS = ["Engineering", "Billing", "Product", "Onboarding"]
    TEAM_W = [0.30, 0.25, 0.25, 0.20]

    PRIORITIES = ["P1", "P2", "P3"]
    PRIO_W = [0.15, 0.35, 0.50]

    CATEGORIES = ["Bug", "Feature Request", "Account", "Billing", "Integration"]
    CAT_W = [0.25, 0.20, 0.20, 0.20, 0.15]

    # SLA breach probability per priority
    SLA_BREACH_P = {"P1": 0.10, "P2": 0.26, "P3": 0.44}

    # Resolution hours ranges per priority (when resolved)
    RES_HOURS = {
        "P1": (0.4, 4.0),
        "P2": (1.5, 20.0),
        "P3": (6.0, 68.0),
    }

    rows = []
    all_days = list(date_range(start, end))
    for d in all_days:
        n = rng.choices([1, 2, 3], weights=[0.45, 0.40, 0.15])[0]
        for _ in range(n):
            team = weighted_choice(rng, TEAMS, TEAM_W)
            priority = weighted_choice(rng, PRIORITIES, PRIO_W)
            category = weighted_choice(rng, CATEGORIES, CAT_W)

            # ~12% of tickets are unresolved (open/pending)
            resolved = rng.random() > 0.12
            if resolved:
                raw_hours = rng.uniform(*RES_HOURS[priority])
                resolution_hours = round(raw_hours, 1)
                breached = "true" if rng.random() < SLA_BREACH_P[priority] else "false"
                # CSAT: higher resolution time → lower score
                max_h = RES_HOURS[priority][1]
                base_csat = 5 - 3 * (raw_hours / max_h)
                csat = max(1, min(5, round(base_csat + rng.uniform(-0.5, 0.5))))
            else:
                resolution_hours = ""
                breached = ""
                csat = ""

            hour = rng.randint(8, 18)
            minute = rng.randint(0, 59)
            created_at = f"{d.isoformat()} {hour:02d}:{minute:02d}"

            rows.append({
                "created_at": created_at,
                "team": team,
                "priority": priority,
                "category": category,
                "sla_breached": breached,
                "resolution_hours": resolution_hours,
                "csat": csat,
            })
    return rows


# ── saas_funnel.csv ───────────────────────────────────────────────────────────

def gen_saas_funnel(rng: random.Random) -> list[dict]:
    start = date(2025, 7, 1)
    end = date(2026, 2, 28)

    CHANNELS = ["Organic", "Paid Search", "Referral", "Partner", "Social"]
    CHAN_W = [0.35, 0.25, 0.20, 0.10, 0.10]

    PLANS = ["Starter", "Pro", "Enterprise"]
    PLAN_W = [0.40, 0.42, 0.18]
    PLAN_MRR = {"Starter": 29, "Pro": 99, "Enterprise": 499}

    rows = []
    all_days = list(date_range(start, end))
    for d in all_days:
        # ~1-2 signups per day
        n = rng.choices([0, 1, 2, 3], weights=[0.15, 0.50, 0.25, 0.10])[0]
        for _ in range(n):
            channel = weighted_choice(rng, CHANNELS, CHAN_W)

            trial_started = "true" if rng.random() < 0.95 else "false"

            if trial_started == "true":
                converted_paid = "true" if rng.random() < 0.41 else "false"
            else:
                converted_paid = "false"

            if converted_paid == "true":
                plan = weighted_choice(rng, PLANS, PLAN_W)
                mrr = PLAN_MRR[plan]
                churned = "true" if rng.random() < 0.17 else "false"
            else:
                plan = ""
                mrr = 0
                churned = "false"

            rows.append({
                "signup_date": d.isoformat(),
                "acquisition_channel": channel,
                "plan": plan,
                "trial_started": trial_started,
                "converted_paid": converted_paid,
                "churned": churned,
                "mrr": mrr,
            })
    return rows


# ── Write ─────────────────────────────────────────────────────────────────────

def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {path.name}: {len(rows)} rows")


def main():
    rng = random.Random(SEED)

    print("Generating sample data...")
    retail = gen_retail_sales(rng)
    tickets = gen_support_tickets(rng)
    funnel = gen_saas_funnel(rng)

    write_csv(OUT / "retail_sales.csv", retail)
    write_csv(OUT / "support_tickets.csv", tickets)
    write_csv(OUT / "saas_funnel.csv", funnel)

    # Print summary statistics for use in expected_outputs.yml
    print("\n── retail_sales summary ──")
    total_rev = sum(r["revenue"] for r in retail)
    total_margin = sum(r["margin"] for r in retail)
    print(f"  rows: {len(retail)}")
    print(f"  total revenue: {total_rev:.2f}")
    print(f"  total margin: {total_margin:.2f}")
    print(f"  margin rate: {total_margin / total_rev * 100:.2f}%")
    by_product = {}
    for r in retail:
        by_product.setdefault(r["product"], 0)
        by_product[r["product"]] += r["revenue"]
    for p, v in sorted(by_product.items(), key=lambda x: -x[1]):
        print(f"  {p}: {v:.2f}")

    print("\n── support_tickets summary ──")
    resolved = [t for t in tickets if t["sla_breached"] in ("true", "false")]
    breached = [t for t in resolved if t["sla_breached"] == "true"]
    csat_vals = [float(t["csat"]) for t in tickets if t["csat"] != ""]
    print(f"  rows: {len(tickets)}")
    print(f"  resolved: {len(resolved)}")
    print(f"  sla breached: {len(breached)} ({len(breached)/len(resolved)*100:.1f}%)")
    print(f"  avg csat: {sum(csat_vals)/len(csat_vals):.2f}")
    by_prio = {}
    for t in tickets:
        by_prio.setdefault(t["priority"], 0)
        by_prio[t["priority"]] += 1
    print(f"  by priority: {dict(sorted(by_prio.items()))}")

    print("\n── saas_funnel summary ──")
    total_signups = len(funnel)
    converted = [u for u in funnel if u["converted_paid"] == "true"]
    churned = [u for u in converted if u["churned"] == "true"]
    total_mrr = sum(u["mrr"] for u in converted if u["churned"] != "true")
    print(f"  rows: {total_signups}")
    print(f"  converted: {len(converted)} ({len(converted)/total_signups*100:.1f}%)")
    print(f"  churned: {len(churned)} ({len(churned)/max(len(converted),1)*100:.1f}% of converted)")
    print(f"  active mrr: {total_mrr}")
    by_chan = {}
    for u in funnel:
        by_chan.setdefault(u["acquisition_channel"], 0)
        by_chan[u["acquisition_channel"]] += 1
    for c, v in sorted(by_chan.items(), key=lambda x: -x[1]):
        print(f"  {c}: {v}")


if __name__ == "__main__":
    main()
