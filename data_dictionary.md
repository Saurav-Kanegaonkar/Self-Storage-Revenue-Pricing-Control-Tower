# Data Dictionary

| Table | Grain | Purpose |
|---|---|---|
| `stores.csv` | Store market | Market metadata, current occupancy, demand, competitor price position, supply pressure, and data quality. |
| `weekly_market_signals.csv` | Store market x week | Demand pace, occupancy movement, move-ins, move-outs, conversion, competitor index, and promotion depth. |
| `pricing_recommendations.csv` | Store market x unit type | Explainable pricing output with current rate, competitor median, recommended rate, elasticity, expected annual revenue delta, confidence, and priority score. |
| `field_feedback.csv` | Feedback item | Local field context that validates, challenges, or delays pricing recommendations. |
| `data_quality_checks.csv` | Source-control check | QA results that determine whether a recommendation can be implemented or needs source remediation first. |
| `analysis/outputs/priority_queue.csv` | Recommendation | Top 30 pricing actions for the weekly revenue-management review. |
