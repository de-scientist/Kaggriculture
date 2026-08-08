# Technical Debt Register

Stage 1 technical debt tracking. All items are deferred to future stages.

| # | Issue | Impact | Priority | Workaround | Planned Stage | Owner |
|---|---|---|---|---|---|---|
| 1 | No multi-turn planning (single-turn lookahead only) | Medium | Medium | N/A — baseline strategy is reactive | Stage 2 | — |
| 2 | No market forecasting | Medium | Medium | Sell immediately, buy seeds when low | Stage 2 | — |
| 3 | Simple greedy pathfinding | Low | Low | Direct movement toward targets | Stage 2 | — |
| 4 | No incremental observation parsing (full GameState rebuild each turn) | Low | Low | Acceptable at 5ms budget | Stage 2 | — |
| 5 | No opponent modeling | Medium | Medium | Ignore opponent state | Stage 3 | — |
| 6 | Static scoring weights | Medium | Medium | Fixed weights from scoring.py | Stage 3 | — |
| 7 | No dynamic strategy switching | Low | Low | Baseline always active | Stage 3 | — |
| 8 | Full 720-turn Kaggle episode not run in CI | Low | Low | Manual validation via validate_submission.py | Stage 2 | — |
| 9 | Market price curve understanding is simplified | Medium | Medium | Approximate with current price | Stage 2 | — |
| 10 | No crop profitability optimization across multiple cycles | Medium | Medium | Fixed planting strategy | Stage 2 | — |
| 11 | Weed removal is reactive, not proactive | Low | Low | DIG when encountered | Stage 2 | — |
| 12 | Land expansion strategy is basic (cheapest quadrant first) | Low | Low | Unlock NE → SW → SE | Stage 2 | — |

## Notes

- Stage 1 is intentionally a correctness and reliability baseline.
- No items are critical (would block submission).
- All deferrals are documented in `docs/competition/competition_notes.md`.
