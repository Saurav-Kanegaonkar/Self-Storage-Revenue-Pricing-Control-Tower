import csv
import json
import math
import random
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ANALYSIS = ROOT / "analysis"
OUTPUTS = ANALYSIS / "outputs"
DOC_IMAGES = ROOT / "docs" / "images"
random.seed(47)


def clamp(value, low, high):
    return max(low, min(high, value))


def money(value):
    return f"${value:,.0f}"


def pct(value):
    return f"{value:+.1f}%"


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


metros = [
    ("PHL", "Philadelphia PA", "Mid-Atlantic", "Urban infill", 1.16, 0.91),
    ("BOS", "Boston MA", "Northeast", "Urban infill", 1.28, 0.88),
    ("NYN", "Northern New Jersey", "Northeast", "Urban infill", 1.34, 0.86),
    ("ATL", "Atlanta GA", "Southeast", "Suburban growth", 1.02, 1.08),
    ("MIA", "Miami FL", "Southeast", "Urban infill", 1.22, 0.94),
    ("ORL", "Orlando FL", "Southeast", "Seasonal leisure", 1.05, 1.02),
    ("TPA", "Tampa FL", "Southeast", "Seasonal leisure", 1.07, 1.00),
    ("DAL", "Dallas TX", "South Central", "Suburban growth", 0.98, 1.12),
    ("HOU", "Houston TX", "South Central", "Suburban growth", 0.94, 1.14),
    ("PHX", "Phoenix AZ", "West", "Suburban growth", 1.04, 1.10),
    ("LAX", "Los Angeles CA", "West", "Urban infill", 1.38, 0.87),
    ("SDG", "San Diego CA", "West", "Urban infill", 1.31, 0.89),
    ("CHI", "Chicago IL", "Midwest", "Mixed urban", 1.08, 0.99),
    ("CLT", "Charlotte NC", "Southeast", "Suburban growth", 0.99, 1.06),
]

unit_types = [
    ("5x5 Interior", 25, 63, 0.35, 0.78),
    ("5x10 Climate", 50, 108, 0.55, 0.92),
    ("10x10 Climate", 100, 178, 0.78, 1.00),
    ("10x15 Drive-Up", 150, 229, 0.88, 1.08),
    ("10x20 Drive-Up", 200, 292, 1.0, 1.16),
]

stores = []
for i in range(42):
    code, metro, region, market_type, price_mult, supply_mult = metros[i % len(metros)]
    sq_ft = random.randrange(52000, 106000, 1000)
    store_age = random.choice(["Lease-up", "Stabilized", "Mature"])
    climate_share = clamp(random.gauss(0.54, 0.12), 0.25, 0.78)
    base_occupancy = {"Lease-up": 78, "Stabilized": 89, "Mature": 92}[store_age]
    occupancy = clamp(random.gauss(base_occupancy, 5.5), 67, 98)
    demand = clamp(random.gauss(100, 14) + (price_mult - 1) * 24, 66, 139)
    comp_gap = clamp(random.gauss(0, 7) + (occupancy - 88) * -0.22, -18, 21)
    supply_pressure = clamp(random.gauss(58, 16) * supply_mult, 22, 93)
    data_quality = clamp(random.gauss(88, 7) - max(0, supply_pressure - 78) * 0.35, 61, 99)
    stores.append(
        {
            "store_id": f"STO{i + 1:03d}",
            "market": metro,
            "region": region,
            "market_type": market_type,
            "store_age": store_age,
            "rentable_sqft": sq_ft,
            "climate_control_share": round(climate_share, 2),
            "current_occupancy_pct": round(occupancy, 1),
            "demand_index": round(demand, 1),
            "competitor_price_gap_pct": round(comp_gap, 1),
            "supply_pressure_index": round(supply_pressure, 1),
            "data_quality_score": round(data_quality, 1),
            "field_owner": random.choice(["North field team", "East field team", "South field team", "West field team"]),
        }
    )


weekly_signals = []
start = date(2026, 1, 5)
for store in stores:
    for week in range(16):
        seasonal = 1 + 0.09 * math.sin((week - 3) / 15 * math.pi)
        demand = clamp(float(store["demand_index"]) * seasonal + random.gauss(0, 5), 55, 150)
        occupancy = clamp(float(store["current_occupancy_pct"]) + random.gauss(0, 1.8) + (week - 8) * 0.08, 62, 99)
        leads = max(18, int(random.gauss(demand * 1.9, 18)))
        move_ins = max(5, int(leads * clamp(random.gauss(0.27, 0.05), 0.15, 0.42)))
        move_outs = max(3, int(move_ins * clamp(random.gauss(0.82, 0.12), 0.55, 1.25)))
        weekly_signals.append(
            {
                "week_start": (start + timedelta(days=week * 7)).isoformat(),
                "store_id": store["store_id"],
                "occupancy_pct": round(occupancy, 1),
                "lead_count": leads,
                "move_in_count": move_ins,
                "move_out_count": move_outs,
                "net_rentals": move_ins - move_outs,
                "web_conversion_pct": round(clamp(random.gauss(18, 3) + (demand - 100) * 0.03, 8, 29), 1),
                "competitor_price_index": round(100 + float(store["competitor_price_gap_pct"]) * -0.8 + random.gauss(0, 4), 1),
                "promo_depth_pct": round(clamp(random.gauss(7, 4) + max(0, 86 - occupancy) * 0.25, 0, 24), 1),
            }
        )


pricing_rows = []
for store in stores:
    for unit_type, sqft, base_rate, elasticity_base, unit_mult in unit_types:
        occupancy = clamp(float(store["current_occupancy_pct"]) + random.gauss(0, 4) + (unit_mult - 1) * 4, 58, 99)
        current_rate = base_rate * unit_mult * (float(store["demand_index"]) / 100) ** 0.28
        current_rate *= 1 + float(store["competitor_price_gap_pct"]) / 140
        current_rate = round(current_rate, 0)
        comp_median = round(current_rate / (1 + float(store["competitor_price_gap_pct"]) / 100), 0)
        lead_pace = clamp(float(store["demand_index"]) + random.gauss(0, 7), 52, 151)
        seasonality = clamp(100 + 12 * math.sin((unit_mult + len(unit_type)) / 8), 86, 116)
        data_quality = float(store["data_quality_score"])
        competitor_gap = (current_rate - comp_median) / comp_median * 100
        elasticity = round(-(elasticity_base + random.random() * 0.55), 2)

        if data_quality < 76:
            action = "Fix source before pricing"
            change_pct = 0
        elif occupancy >= 93 and lead_pace >= 104 and competitor_gap <= 8:
            action = "Raise street rate"
            change_pct = clamp(2.5 + (occupancy - 92) * 0.7 + (lead_pace - 100) * 0.05 - max(0, competitor_gap) * 0.08, 2, 9)
        elif occupancy <= 82 and lead_pace < 95:
            action = "Protect occupancy"
            change_pct = -clamp(2.5 + (84 - occupancy) * 0.45 + (95 - lead_pace) * 0.05, 2, 8)
        elif competitor_gap >= 12 and occupancy < 90:
            action = "Hold rate and test promo"
            change_pct = -1.5
        elif occupancy >= 90 and competitor_gap < -6:
            action = "Narrow competitor gap"
            change_pct = clamp(2 + abs(competitor_gap) * 0.2, 2, 7)
        else:
            action = "Hold with watchlist"
            change_pct = 0

        occupied_units = random.randint(44, 190)
        vacant_units = max(2, int(occupied_units * (100 - occupancy) / max(occupancy, 1)))
        new_rate = round(current_rate * (1 + change_pct / 100), 0)
        expected_demand_change = elasticity * change_pct
        if change_pct > 0:
            # Street-rate changes affect new rentals and renewals gradually, not the full occupied base at once.
            demand_drag = current_rate * occupied_units * max(0, -expected_demand_change) / 100 * 0.14
            monthly_delta = (new_rate - current_rate) * occupied_units * 0.58 - demand_drag
        elif change_pct < 0:
            protected_demand = current_rate * max(vacant_units, 1) * min(0.45, abs(expected_demand_change) / 100)
            churn_protection = current_rate * occupied_units * 0.015
            promo_cost = (current_rate - new_rate) * occupied_units * 0.08
            monthly_delta = protected_demand + churn_protection - promo_cost
        else:
            monthly_delta = 0
        annual_delta = monthly_delta * 12
        confidence = clamp(
            data_quality * 0.52
            + (100 - abs(competitor_gap)) * 0.18
            + min(100, lead_pace) * 0.16
            + (100 - float(store["supply_pressure_index"])) * 0.14,
            42,
            97,
        )
        priority = (
            abs(annual_delta) / 850
            + max(0, occupancy - 89) * 2.2
            + max(0, 86 - occupancy) * 1.8
            + max(0, 72 - data_quality) * 3.5
            + max(0, abs(competitor_gap) - 7) * 1.7
        )
        pricing_rows.append(
            {
                "store_id": store["store_id"],
                "market": store["market"],
                "unit_type": unit_type,
                "occupancy_pct": round(occupancy, 1),
                "current_rate": int(current_rate),
                "competitor_median_rate": int(comp_median),
                "competitor_gap_pct": round(competitor_gap, 1),
                "lead_pace_index": round(lead_pace, 1),
                "seasonality_index": round(seasonality, 1),
                "elasticity": elasticity,
                "recommended_action": action,
                "recommended_rate": int(new_rate),
                "rate_change_pct": round(change_pct, 1),
                "expected_annual_revenue_delta": int(round(annual_delta, 0)),
                "confidence_score": round(confidence, 1),
                "priority_score": round(priority, 1),
                "occupied_units": int(occupied_units),
                "vacant_units": int(vacant_units),
            }
        )


pricing_rows.sort(key=lambda row: float(row["priority_score"]), reverse=True)

feedback_templates = [
    ("Competitive concession", "Local manager reports a nearby operator added first-month promotion."),
    ("Lead quality", "Field team sees more quote shoppers than booked rentals this week."),
    ("Unit scarcity", "Store has limited availability in the requested unit type."),
    ("Move-out pressure", "Manager expects student or apartment turnover to raise move-outs next week."),
    ("Access friction", "Gate or elevator issue may be suppressing conversion until resolved."),
]
field_feedback = []
for row in pricing_rows[:54]:
    signal, note = random.choice(feedback_templates)
    field_feedback.append(
        {
            "feedback_id": f"FF{len(field_feedback) + 1:03d}",
            "store_id": row["store_id"],
            "market": row["market"],
            "unit_type": row["unit_type"],
            "signal": signal,
            "field_note": note,
            "pricing_response": row["recommended_action"],
            "status": random.choice(["Incorporated", "Needs analyst review", "Waiting on field confirmation"]),
        }
    )


quality_checks = []
for store in stores:
    issues = [
        ("competitor_rate_freshness", "Competitor scrape older than review threshold"),
        ("unit_inventory_variance", "PMS inventory total differs from pricing mart"),
        ("promo_code_mapping", "Promotion flag missing from market feed"),
        ("lead_source_completeness", "Web and phone leads not reconciled"),
    ]
    for check_name, desc in random.sample(issues, k=2):
        score = clamp(random.gauss(float(store["data_quality_score"]), 8), 45, 100)
        quality_checks.append(
            {
                "check_id": f"DQ{len(quality_checks) + 1:03d}",
                "store_id": store["store_id"],
                "market": store["market"],
                "check_name": check_name,
                "result": "Pass" if score >= 82 else "Watch" if score >= 70 else "Blocker",
                "score": round(score, 1),
                "business_impact": desc,
            }
        )


DATA.mkdir(exist_ok=True)
ANALYSIS.mkdir(exist_ok=True)
OUTPUTS.mkdir(parents=True, exist_ok=True)
DOC_IMAGES.mkdir(parents=True, exist_ok=True)

write_csv(DATA / "stores.csv", stores)
write_csv(DATA / "weekly_market_signals.csv", weekly_signals)
write_csv(DATA / "pricing_recommendations.csv", pricing_rows)
write_csv(DATA / "field_feedback.csv", field_feedback)
write_csv(DATA / "data_quality_checks.csv", quality_checks)
write_csv(OUTPUTS / "priority_queue.csv", pricing_rows[:30])

top = pricing_rows[0]
raise_count = sum(1 for row in pricing_rows if row["recommended_action"] in ["Raise street rate", "Narrow competitor gap"])
protect_count = sum(1 for row in pricing_rows if row["recommended_action"] == "Protect occupancy")
source_fix_count = sum(1 for row in pricing_rows if row["recommended_action"] == "Fix source before pricing")
expected_delta = sum(row["expected_annual_revenue_delta"] for row in pricing_rows[:30])
avg_confidence = sum(row["confidence_score"] for row in pricing_rows[:30]) / 30
avg_occ = sum(float(store["current_occupancy_pct"]) for store in stores) / len(stores)

summary = {
    "top_market": top["market"],
    "top_unit_type": top["unit_type"],
    "top_action": top["recommended_action"],
    "top_rate_change_pct": top["rate_change_pct"],
    "top_expected_annual_revenue_delta": top["expected_annual_revenue_delta"],
    "raise_count": raise_count,
    "protect_count": protect_count,
    "source_fix_count": source_fix_count,
    "expected_delta_top_30": expected_delta,
    "avg_confidence_top_30": round(avg_confidence, 1),
    "avg_store_occupancy": round(avg_occ, 1),
}

(ROOT / "src").mkdir(exist_ok=True)
(ROOT / "src" / "data.js").write_text(
    "const PRICING_DATA = "
    + json.dumps(
        {
            "stores": stores,
            "weeklySignals": weekly_signals,
            "pricingRecommendations": pricing_rows,
            "fieldFeedback": field_feedback,
            "qualityChecks": quality_checks,
            "summary": summary,
        },
        indent=2,
    )
    + ";\n",
    encoding="utf-8",
)

(DATA / "README.md").write_text(
    """# Data Sources

All datasets are deterministic synthetic data for a public portfolio artifact. They are modeled on the structure of a national self-storage revenue-management workflow, not on any real operator performance.

- `stores.csv`: 42 store-market records with region, market type, rentable square feet, occupancy, demand index, competitor price gap, supply pressure, data quality, and field ownership.
- `weekly_market_signals.csv`: 672 store-week rows with occupancy, lead count, move-ins, move-outs, conversion, competitor index, and promotion depth.
- `pricing_recommendations.csv`: 210 store-by-unit-type pricing recommendations with current rate, competitor median, lead pace, seasonality, elasticity, recommended rate, expected annual revenue delta, confidence, and priority score.
- `field_feedback.csv`: 54 district-manager style feedback records tied to the highest-priority recommendations.
- `data_quality_checks.csv`: 84 source-control checks covering competitor rate freshness, inventory reconciliation, promotion mapping, and lead-source completeness.

The generator uses a fixed random seed. Rates are built from unit-size baseline prices, market multipliers, demand indices, competitor gaps, and unit occupancy. Recommendation logic uses occupancy bands, lead pace, competitor position, seasonality, elasticity, and data-quality confidence. This makes the artifact reproducible and interview-defensible without exposing private pricing data.
""",
    encoding="utf-8",
)

(ROOT / "data_dictionary.md").write_text(
    """# Data Dictionary

| Table | Grain | Purpose |
|---|---|---|
| `stores.csv` | Store market | Market metadata, current occupancy, demand, competitor price position, supply pressure, and data quality. |
| `weekly_market_signals.csv` | Store market x week | Demand pace, occupancy movement, move-ins, move-outs, conversion, competitor index, and promotion depth. |
| `pricing_recommendations.csv` | Store market x unit type | Explainable pricing output with current rate, competitor median, recommended rate, elasticity, expected annual revenue delta, confidence, and priority score. |
| `field_feedback.csv` | Feedback item | Local field context that validates, challenges, or delays pricing recommendations. |
| `data_quality_checks.csv` | Source-control check | QA results that determine whether a recommendation can be implemented or needs source remediation first. |
| `analysis/outputs/priority_queue.csv` | Recommendation | Top 30 pricing actions for the weekly revenue-management review. |
""",
    encoding="utf-8",
)

(ANALYSIS / "analysis_plan.md").write_text(
    """# Analysis Plan

1. Build a store-market base table with occupancy, demand, competitor price position, supply pressure, and data-quality scores.
2. Generate weekly demand and movement signals so price decisions are tied to lead pace, move-ins, move-outs, conversion, and promotion depth.
3. Score each store-by-unit-type combination with an explainable pricing model that uses occupancy bands, competitor gap, lead pace, seasonality, elasticity, and source confidence.
4. Rank recommendations by expected revenue movement, occupancy risk, competitor mismatch, and data-quality blockers.
5. Attach field feedback and source checks so recommendations are not implemented blindly.
6. Summarize the output into an executive queue, market signal view, and guardrail view.
""",
    encoding="utf-8",
)

(ANALYSIS / "executive_findings.md").write_text(
    f"""# Executive Findings

## What I Analyzed

I generated a self-storage revenue-management mart with {len(stores)} store markets, {len(weekly_signals)} weekly signal rows, {len(pricing_rows)} unit-level pricing recommendations, {len(field_feedback)} field feedback records, and {len(quality_checks)} source-control checks.

## Findings

- The top recommendation is {top['top_action'] if 'top_action' in top else top['recommended_action']} for {top['top_unit_type'] if 'top_unit_type' in top else top['unit_type']} in {top['market']}, with a {pct(float(top['rate_change_pct']))} rate move and {money(top['expected_annual_revenue_delta'])} expected annual revenue impact.
- The top 30 queue totals {money(expected_delta)} in modeled annual revenue movement with {avg_confidence:.1f} average confidence.
- {raise_count} recommendations raise or narrow underpriced rates, {protect_count} protect occupancy, and {source_fix_count} require source remediation before pricing action.
- The workflow is strongest where pricing output, field context, and source-quality checks agree. Where they disagree, the artifact routes the item to analyst review instead of forcing a price move.

## Recommendation

Use the priority queue as the weekly revenue-management operating artifact. Start with high-confidence rate moves, keep occupancy-protection items on watch, and block any recommendation whose competitor or inventory source check is below threshold.
""",
    encoding="utf-8",
)

(ANALYSIS / "sql_checks.sql").write_text(
    """-- Portfolio SQL checks written against the synthetic CSV tables.

-- 1. Find pricing recommendations blocked by low source quality.
select
  pr.store_id,
  pr.market,
  pr.unit_type,
  pr.recommended_action,
  pr.confidence_score,
  dq.check_name,
  dq.result
from pricing_recommendations pr
join data_quality_checks dq
  on pr.store_id = dq.store_id
where dq.result = 'Blocker'
order by pr.priority_score desc;

-- 2. Rank high-occupancy underpriced unit types.
select
  store_id,
  market,
  unit_type,
  occupancy_pct,
  competitor_gap_pct,
  recommended_rate,
  expected_annual_revenue_delta
from pricing_recommendations
where occupancy_pct >= 92
  and competitor_gap_pct < 0
order by expected_annual_revenue_delta desc;

-- 3. Summarize weekly demand pace by market.
select
  s.market,
  avg(w.occupancy_pct) as avg_occupancy_pct,
  sum(w.lead_count) as lead_count,
  sum(w.net_rentals) as net_rentals,
  avg(w.promo_depth_pct) as avg_promo_depth_pct
from weekly_market_signals w
join stores s
  on w.store_id = s.store_id
group by s.market
order by lead_count desc;
""",
    encoding="utf-8",
)

(ROOT / "STATUS.md").write_text(
    """# Status

- Status: upgraded through the Portfolio Artifact Upgrade Workflow.
- Target role fit: pricing analyst, revenue management, self-storage dynamic pricing.
- Public README uses company-domain language rather than naming the target company.
- Synthetic data is documented and reproducible from `scripts/score_operating_data.py`.
- Screenshots are stored in `docs/images/` after visual verification.
""",
    encoding="utf-8",
)

readme = f"""# Self-Storage Revenue Pricing Control Tower

An interactive portfolio artifact for a national self-storage revenue-management team that needs a weekly pricing cadence across many store locations. The control tower connects occupancy, lead pace, competitor price position, seasonal demand, unit-type availability, field feedback, and source-quality checks into one explainable pricing recommendation workflow.

## Screenshots

![Executive pricing queue](docs/images/pricing-queue.png)

The pricing queue ranks store-by-unit-type recommendations by expected revenue movement, confidence, occupancy risk, and competitor price gap.

![Market and competitor signals](docs/images/market-signals.png)

The market signal view shows where occupancy, lead pace, competitor position, promotion depth, and supply pressure support or challenge a rate move.

![Guardrails and field alignment](docs/images/guardrails.png)

The guardrail view connects model drivers, data-quality checks, and field feedback so pricing actions are implemented only when the evidence is strong enough.

## What This Project Demonstrates

This project shows how a pricing analyst can move beyond static reporting and operate a defensible revenue-management workflow:

- Identify dynamic pricing actions by store, market, and unit type.
- Balance rate growth against occupancy protection.
- Use competitor pricing and seasonal demand signals to explain recommendations.
- Track source-quality blockers before actioning a price change.
- Incorporate local field feedback into a pricing review cadence.
- Prepare stakeholder-ready reporting that translates analytics into next steps.

## Data

The data is deterministic synthetic data generated by `scripts/score_operating_data.py`. It does not represent real company, customer, facility, competitor, or financial performance. Synthetic data is used because live self-storage pricing is local, dynamic, and commercially sensitive.

The generator creates:

- 42 store-market records with region, market type, rentable square feet, occupancy, demand index, competitor price gap, supply pressure, and data quality.
- 672 weekly market-signal rows with occupancy, leads, move-ins, move-outs, conversion, competitor index, and promotion depth.
- 210 store-by-unit-type pricing recommendations with current rate, competitor median, elasticity, recommended rate, expected annual revenue delta, confidence, and priority score.
- 54 field feedback records that simulate district-manager context.
- 84 source-control checks covering competitor rate freshness, unit inventory reconciliation, promotion mapping, and lead-source completeness.

Rates are synthesized from unit-size baselines, market multipliers, occupancy bands, demand pace, competitor gaps, seasonality, promotion pressure, and elasticity assumptions. Recommendation logic is intentionally explainable: raise when occupancy and demand are strong, protect occupancy when weak demand coincides with vacancy pressure, hold or test promotion when competitor gaps are unfavorable, and block recommendations when source quality is below threshold.

## Analysis Outputs

- `analysis/outputs/priority_queue.csv`: top 30 pricing actions for review.
- `analysis/executive_findings.md`: concise findings and recommendation.
- `analysis/analysis_plan.md`: modeling and workflow plan.
- `analysis/sql_checks.sql`: SQL-style validation checks for blocked recommendations, underpriced high-occupancy units, and market demand summaries.
- `data_dictionary.md`: table grains and field purposes.

## Role Fit

The artifact is designed for a pricing and revenue-management analyst role. It demonstrates the work behind setting and updating prices across a large store network: analyzing store-specific characteristics, monitoring seasonal demand and competitor strategies, creating clear reports, and aligning recommendations with field operations.

## Run Locally

```bash
python3 scripts/score_operating_data.py
python3 -m http.server 49271
```

Then open `http://localhost:49271`.

## Scope

This is a static portfolio artifact with reproducible synthetic data and transparent rules-based scoring. It does not connect to live property-management systems, competitor scrape feeds, pricing engines, finance systems, customer records, or production approval workflows. It does show how a pricing analyst can structure a repeatable operating artifact for dynamic pricing, market monitoring, source validation, and stakeholder-ready action planning.
"""
(ROOT / "README.md").write_text(readme, encoding="utf-8")

print(f"Generated {len(stores)} stores, {len(weekly_signals)} weekly rows, and {len(pricing_rows)} pricing recommendations.")
print(f"Top queue impact: {money(expected_delta)} across 30 recommendations.")
