# Competitive Baseline (Stage 4B)

Champion under test: **champion-v1.0** (EndgamePolicy).

- Version: champion-v1.0
- Commit: 1f9356f8ef917c90996e59fef6906c166b7f4695
- Average Final Coins: 17755.0
- Median Final Coins: 20798.0
- Best Final Coins: 22243.0
- Worst Final Coins: 8193.0
- Wins: 20  Losses: 4  Ties: 3
- Win Rate: 74.1%
- Average Runtime/turn (ms): 1.607
- Maximum Runtime/turn (ms): 345.325
- Invalid Actions: 0 (planner emits legal actions)
- Fallback Activations: 0

### Per-opponent

| Opponent | Games | Wins | Losses | Ties | Win Rate | Avg Coins | Avg Margin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aggressive | 3 | 3 | 0 | 0 | 100.0% (100-100) | 21267.33 | 19385.33 |
| champion | 3 | 0 | 0 | 3 | 0.0% (0-0) | 10036.67 | 0.00 |
| conservative | 3 | 3 | 0 | 0 | 100.0% (100-100) | 20913.67 | 18039.00 |
| expansion | 3 | 3 | 0 | 0 | 100.0% (100-100) | 21056.00 | 20474.67 |
| market | 3 | 2 | 1 | 0 | 66.7% (13-100) | 13406.00 | 3006.67 |
| no_endgame | 3 | 0 | 3 | 0 | 0.0% (0-0) | 9889.00 | -2355.67 |
| production | 3 | 3 | 0 | 0 | 100.0% (100-100) | 21002.33 | 17250.33 |
| random | 3 | 3 | 0 | 0 | 100.0% (100-100) | 21424.67 | 21421.33 |
| starter | 3 | 3 | 0 | 0 | 100.0% (100-100) | 20799.33 | 17423.67 |

### Known Strengths
- Wins 20/21 vs diverse heuristic opponents.
- Zero fallback activations across all matches (robust).
- Sub-3ms average decision time; far below any execution limit.

### Known Weaknesses
- Lost 1/3 to the market-oriented opponent (early liquidation may crash prices).
- Ablation shows EndgamePolicy's liquidation REDUCES terminal coins vs the pure champion (see CHAMPION_HISTORY).
