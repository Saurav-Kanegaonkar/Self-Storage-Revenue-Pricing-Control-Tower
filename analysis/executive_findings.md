# Executive Findings

## What I Analyzed

I generated a self-storage revenue-management mart with 42 store markets, 672 weekly signal rows, 210 unit-level pricing recommendations, 54 field feedback records, and 84 source-control checks.

## Findings

- The top recommendation is Raise street rate for 10x15 Drive-Up in Los Angeles CA, with a +8.7% rate move and $13,215 expected annual revenue impact.
- The top 30 queue totals $259,067 in modeled annual revenue movement with 80.7 average confidence.
- 36 recommendations raise or narrow underpriced rates, 25 protect occupancy, and 10 require source remediation before pricing action.
- The workflow is strongest where pricing output, field context, and source-quality checks agree. Where they disagree, the artifact routes the item to analyst review instead of forcing a price move.

## Recommendation

Use the priority queue as the weekly revenue-management operating artifact. Start with high-confidence rate moves, keep occupancy-protection items on watch, and block any recommendation whose competitor or inventory source check is below threshold.
