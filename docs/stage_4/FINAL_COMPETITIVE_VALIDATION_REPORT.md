# Final Competitive Validation Report (Stage 4B)

## Executive Summary
Stage 4B validated the champion under fair, multi-seed, multi-opponent benchmarks and
used an evidence-based ablation to replace EndgamePolicy with the pure champion.

## Champion Version
**champion-v1.1** (ChampionPolicy, no endgame).

## Evaluation Protocol
- 720-turn episodes via kaggle_environments.
- 3 seeds per matchup (diverse opponents) unless noted.
- Our agent always player 0, instrumented for latency + fallback.

## Opponents
random, starter, conservative, aggressive, expansion, production, market (all our planner presets or built-ins).

## Number of Games
- champion-v1.0: 27  |  champion-v1.1: 21  |  challengers: 24

## Win Rate (champion-v1.1): 100.0% (21/21)
## Average Final Coins: 22184.1
## Median Final Coins: 22745.0
## Best Result: 24297.0
## Worst Result: 17509.0
## Runtime (avg/max turn ms): 1.912 / 142.011
## Fallback Rate: 0

## Major Strengths
- Robust: 0 fallback activations; always completes 720 turns.
- Dominates all heuristic opponents; fast decisions.

## Known Weaknesses
- Only 3 seeds per matchup; margins vs v1.0 are modest in win-rate terms (coin margin is consistent).
- Not yet tested against real human/submitted competition agents.

## Champion Decision
Promote champion-v1.1 (pure ChampionPolicy). Retire EndgamePolicy and all three challengers (C01/C02/C08).

## Submission Recommendation
READY (pending out-of-repo: competition rules accepted, Kaggle CLI authenticated).
