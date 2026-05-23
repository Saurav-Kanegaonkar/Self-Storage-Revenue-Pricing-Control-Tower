-- Portfolio SQL checks written against the synthetic CSV tables.

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
