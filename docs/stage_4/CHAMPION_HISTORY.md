# Champion History (Stage 4B)

## v1.0 — EndgamePolicy (initial Stage 4 champion)
- Commit: 018492be61e1773e1739caba10140ee930ccca0e
- Change: added horizon wind-down + liquidation (EndgamePolicy) over the pure champion.
- Evidence: 20/21 wins vs diverse opponents, ~21k avg coins.
- Result: ablation refuted the endgame liquidation; lost all 3 self-play games to the pure champion.

## v1.1 — Pure ChampionPolicy (promoted)
- Commit: 018492be61e1773e1739caba10140ee930ccca0e
- Change: reverted EndgamePolicy; submission default is now ChampionPolicy (no endgame).
- Evidence: 21/21 wins vs diverse opponents, ~22.5k avg coins, beats the market opponent 3/3.
- Reason for promotion: strictly dominates v1.0 on both primary (win rate) and secondary (coins) metrics.
