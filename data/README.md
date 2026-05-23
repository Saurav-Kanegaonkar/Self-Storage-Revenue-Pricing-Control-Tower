# Data Sources

All datasets are deterministic synthetic data for a public portfolio artifact. They are modeled on the structure of a national self-storage revenue-management workflow, not on any real operator performance.

- `stores.csv`: 42 store-market records with region, market type, rentable square feet, occupancy, demand index, competitor price gap, supply pressure, data quality, and field ownership.
- `weekly_market_signals.csv`: 672 store-week rows with occupancy, lead count, move-ins, move-outs, conversion, competitor index, and promotion depth.
- `pricing_recommendations.csv`: 210 store-by-unit-type pricing recommendations with current rate, competitor median, lead pace, seasonality, elasticity, recommended rate, expected annual revenue delta, confidence, and priority score.
- `field_feedback.csv`: 54 district-manager style feedback records tied to the highest-priority recommendations.
- `data_quality_checks.csv`: 84 source-control checks covering competitor rate freshness, inventory reconciliation, promotion mapping, and lead-source completeness.

The generator uses a fixed random seed. Rates are built from unit-size baseline prices, market multipliers, demand indices, competitor gaps, and unit occupancy. Recommendation logic uses occupancy bands, lead pace, competitor position, seasonality, elasticity, and data-quality confidence. This makes the artifact reproducible and interview-defensible without exposing private pricing data.
