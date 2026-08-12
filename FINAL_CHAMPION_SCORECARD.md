# Final Champion Scorecard

**Submission champion:** `champion-v1.1` — `ChampionPolicy` (no EndgamePolicy), wrapped in `FailSafeAgent`.
**Commit:** 1f9356f8ef917c90996e59fef6906c166b7f4695

## Champion profile
| Attribute | Value |
| --- | --- |
| Planner | TurnPlanner (champion heuristic) |
| Policy | ChampionPolicy (endgame disabled; market.py still liquidates shed at endgame_sell_day) |
| Fail-safe | FailSafeAgent (2-arg Kaggle-safe) |
| Entry point | main.agent |
| Determinism | Deterministic; model-free |

## Performance scorecard (Stage 4B, 3 seeds/opponent, 720 turns)
- Win rate: 100.0% (42/42)
- Average final coins: 22184.1
- Median final coins: 22745.0
- Best: 24297.0  Worst: 17509.0
- Avg/max decision time: 1.912 / 142.011 ms
- Fallback activations: 0

## Evolution
- champion-v1.0 (EndgamePolicy): 20/21 wins, ~21k avg coins; lost to market opponent and lost all self-play to no_endgame.
- champion-v1.1 (pure ChampionPolicy): 21/21 wins, ~22.5k avg coins; beats market opponent 3/3.

See COMPETITION_COMPLIANCE_CHECKLIST.md and CHAMPION_TOURNAMENT_REPORT.md.
