# Competitive Baseline (Stage 4B)

Champion under test: **champion-v1.0** (EndgamePolicy).

- Version: champion-v1.0
- Commit: 3045af6b305aeebf04c6c001801f18c8990b8b32
- Average Final Coins: 21500.4
- Median Final Coins: 22737.0
- Best Final Coins: 24379.0
- Worst Final Coins: 10623.0
- Wins: 20  Losses: 1  Ties: 0
- Win Rate: 95.2%
- Average Runtime/turn (ms): 1.948
- Maximum Runtime/turn (ms): 108.845
- Invalid Actions: 0 (planner emits legal actions)
- Fallback Activations: 0

### Per-opponent

| Opponent | Games | Wins | Losses | Ties | Win Rate | Avg Coins | Avg Margin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aggressive | 3 | 3 | 0 | 0 | 100.0% (100-100) | 22970.33 | 17916.33 |
| conservative | 3 | 3 | 0 | 0 | 100.0% (100-100) | 23365.33 | 20183.00 |
| expansion | 3 | 3 | 0 | 0 | 100.0% (100-100) | 22264.67 | 18561.67 |
| market | 3 | 2 | 1 | 0 | 66.7% (13-100) | 13693.33 | 3067.00 |
| production | 3 | 3 | 0 | 0 | 100.0% (100-100) | 22899.33 | 17532.33 |
| random | 3 | 3 | 0 | 0 | 100.0% (100-100) | 21988.33 | 21988.33 |
| starter | 3 | 3 | 0 | 0 | 100.0% (100-100) | 23321.33 | 19996.67 |

### Known Strengths
- Wins 20/21 vs diverse heuristic opponents.
- Zero fallback activations across all matches (robust).
- Sub-3ms average decision time; far below any execution limit.

### Known Weaknesses
- Lost 1/3 to the market-oriented opponent (early liquidation may crash prices).
- Ablation shows EndgamePolicy's liquidation REDUCES terminal coins vs the pure champion (see CHAMPION_HISTORY).
