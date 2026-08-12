# Final Champion Scorecard

**Submission champion:** `champion_endgame` — `EndgamePolicy`
(`agent/runtime/policies.py:56`), selected via `ChampionArena`
(`agent/submission/championship.py`).

## Champion profile

| Attribute | Value |
| --- | --- |
| Planner | `agent.runtime.planner.TurnPlanner` (champion heuristic) |
| Policy | `EndgamePolicy` (wind-down day 22, liquidation day 26) |
| Fail-safe | `FailSafeAgent` (`agent/submission/failsafe.py`) — guaranteed legal action |
| Entry point | `main.agent` (delegates to `agent.runtime.agent`) |
| Determinism | Deterministic; no runtime training |
| Model dependency | None (learned layer optional, degrades to champion) |

## Behaviour by season phase

| Phase | Day range | Behaviour |
| --- | --- | --- |
| Growth | 0–21 | Pure champion planner (plant, water, harvest, hire, expand) |
| Wind-down | 22–25 | Stops land/animals, tapers hiring to 2; keeps short crops |
| Liquidation | 26–29 | Stops planting; market endgame logic sells the shed; hands released |

## Performance scorecard (local validation)

| Opponent | Our coins | Result |
| --- | --- | --- |
| `random` | ~20,700 | Win |
| `starter` | ~20,000 | Win |
| self (mirror) | ~10,400 | Tie (expected) |

## Robustness scorecard

| Check | Result |
| --- | --- |
| Imports & callable | PASS |
| Sample observation → legal action | PASS |
| Fail-safe wrapper present | PASS |
| Full validation episode (no error) | PASS (reward > 0, status DONE) |
| mypy `strict` on `agent/` | PASS (198 files) |

See `COMPETITION_COMPLIANCE_CHECKLIST.md` for the machine-generated checklist and
`FINAL_SUBMISSION_MANIFEST.md` for the file inventory.
