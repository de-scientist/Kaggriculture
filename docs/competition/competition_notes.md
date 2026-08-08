# Competition Notes

## Overview

This document records known limitations and assumptions of the Stage 1
Kaggriculture agent.

## Official Interface Status

- **Entry point:** Verified — `main.py` with `agent(obs)` function
  (confirmed by AGENTS.md)
- **Observation format:** Verified — documented fields match the
  Kaggle observation schema
- **Action format:** Verified — `["farmer", "hands", "market"]` structure
  matches Kaggle expectations
- **Environment:** `kaggle-environments` package available on PyPI

## Known Limitations

### Strategy Limitations

1. **No market forecasting** — The agent does not predict price
   movements. It sells immediately when possible.
2. **No multi-turn planning** — Each decision is made independently;
   there is no lookahead beyond the current turn.
3. **No opponent modeling** — The agent ignores opponent state
   (public tiles are visible but not strategically analyzed).
4. **Simple pathfinding** — Workers use greedy nearest-tile navigation.
5. **Static weights** — Scoring weights do not adapt to game state.
6. **No resource buffering** — The agent does not optimize for
   future demand (e.g., saving wheat for animal feed).

### Technical Limitations

1. **Observation parsing performance** — The adapter parses the full
   10×10 tile grid each turn (up to ~5 ms).
2. **No incremental updates** — The full GameState is reconstructed
   each turn; no diff-based parsing.
3. **Single-threaded** — No parallelism in decision making.
4. **Memory allocation** — New domain objects created each turn (GC
   pressure in long episodes).

### Simulation Limitations

1. **No full Kaggle episode test in CI** — Running a full 720-turn
   episode against `kaggle-environments` requires a real game
   environment and is done manually.
2. **Weed spawn randomness** — Random elements are seeded but not
   exhaustively tested across all seeds.
3. **Market dynamics** — The dynamic price function is complex; the
   agent's understanding of price curves is simplified.

### Competition Notes

1. **Submission size** — The competition may have file size limits
   for submissions. The current package should be well within limits.
2. **Execution time limits** — Kaggle may enforce per-turn time limits
   for submissions. The agent targets < 500 ms per decision.
3. **EpisodeSteps** — The environment uses `episodeSteps: 720` (24 × 30).

## Future Improvements (Deferred to Stage 2+)

- Market trend analysis using historical price data
- Multi-turn lookahead planning
- Opponent behavior modeling
- Dynamic scoring weight adjustment
- Incremental observation parsing
- Caching of computed values
