# Competitive Baseline (Stage 4B)

Champion under test: **champion-v1.0** (EndgamePolicy).

- Version: champion-v1.0
- Commit: 018492be61e1773e1739caba10140ee930ccca0e
- Average Final Coins: 19981.3
- Median Final Coins: 20971.0
- Best Final Coins: 22243.0
- Worst Final Coins: 8193.0
- Wins: 20  Losses: 1  Ties: 0
- Win Rate: 95.2%
- Average Runtime/turn (ms): 1.597
- Maximum Runtime/turn (ms): 345.325
- Invalid Actions: 0 (planner emits legal actions)
- Fallback Activations: 0

### Per-opponent

| Opponent | Games | Wins | Losses | Ties | Win Rate | Avg Coins | Avg Margin |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| aggressive | 3 | 3 | 0 | 0 | 100.0% (100-100) | 21267.33 | 19385.33 |
| conservative | 3 | 3 | 0 | 0 | 100.0% (100-100) | 20913.67 | 18039.00 |
| expansion | 3 | 3 | 0 | 0 | 100.0% (100-100) | 21056.00 | 20474.67 |
| market | 3 | 2 | 1 | 0 | 66.7% (13-100) | 13406.00 | 3006.67 |
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
