# Hypothesis Register (Stage 4B)

EndgamePolicy ablation (champion-v1.0 vs no_endgame):

## H-A
- Hypothesis: Stopping land expansion late improves final liquidity.
- Affected: EndgamePolicy
- Experiment: champion vs no_endgame
- Result: Refuted: no_endgame (no land cutoff) won all 21 diverse games at higher coins.
- Decision: RETIRE

## H-B
- Hypothesis: Stopping animal purchases late improves terminal wealth.
- Affected: EndgamePolicy
- Experiment: champion vs no_endgame
- Result: Not isolated; full EndgamePolicy lost to no_endgame. Inconclusive -> no benefit.
- Decision: RETIRE

## H-C
- Hypothesis: Tapering hiring from ~day 22 improves profitability.
- Affected: EndgamePolicy
- Experiment: champion vs no_endgame
- Result: Refuted: no_endgame (no hiring taper) won all diverse games at higher coins.
- Decision: RETIRE

## H-D
- Hypothesis: Stopping planting from ~day 26 improves terminal cash.
- Affected: EndgamePolicy
- Experiment: champion vs no_endgame
- Result: Refuted: champion WITH endgame lost all 3 self-play games to no_endgame (avg 10.5k vs 12.2k).
- Decision: RETIRE

## H-E
- Hypothesis: Late inventory liquidation improves final score.
- Affected: EndgamePolicy
- Experiment: champion vs no_endgame
- Result: Refuted: liquidation reduced terminal cash; market.py sell logic already liquidates.
- Decision: RETIRE
