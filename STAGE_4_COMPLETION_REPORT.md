# Stage 4 Completion Report

**Stage:** Championship Optimization, Final Competitive Agent, Submission
Engineering & Leaderboard Readiness
**Status:** Complete
**Champion:** `champion_endgame` (`EndgamePolicy`) wrapped in `FailSafeAgent`

## Acceptance criteria mapping

| Stage 4 requirement | Delivered | Location |
| --- | --- | --- |
| Baseline selection across Stage 1–3 candidates | Candidate pool + arena + decision | `STAGE_4_BASELINE_SELECTION.md`, `agent/submission/championship.py` |
| Champion / challenger with champion protection | `ChampionArena.select_champion` (margin-guarded) | `agent/submission/championship.py:83` |
| Endgame / horizon-dependent strategy switching | `EndgamePolicy` (wind-down + liquidation) | `agent/runtime/policies.py:56` |
| Risk management / distress handling | Market endgame sell + `EndgamePolicy` liquidation | `agent/runtime/market.py:39`, `policies.py:82` |
| Fail-safe hierarchy (never crash a turn) | `FailSafeAgent` + `legalize` + `EMERGENCY_ACTION` | `agent/submission/failsafe.py` |
| Two-argument Kaggle call tolerance | `FailSafeAgent.__call__(obs, configuration=None)` | `agent/submission/failsafe.py:54` |
| Submission validation checklist (§72) | `submission_check.run_all` | `agent/submission/submission_check.py` |
| Final scorecard | `FINAL_CHAMPION_SCORECARD.md` | root |
| Submission manifest | `FINAL_SUBMISSION_MANIFEST.md` | root |
| Compliance checklist | `COMPETITION_COMPLIANCE_CHECKLIST.md` (generated) | root |
| mypy `strict` compliance | `agent/` clean (198 files) | verified |
| Local end-to-end validation | Wins vs `random`/`starter`, DONE | verified |

## Bugs found and fixed

1. **Submission non-functional (ERROR every game).** The Kaggle environment calls
   `agent(observation, configuration)` with two arguments; the previous
   one-argument wrapper raised `TypeError` outside its try/except, so the
   environment marked the agent `ERROR` and locked reward at 3,000. Fixed by
   giving `FailSafeAgent.__call__` the two-argument signature. This is the
   highest-impact Stage 4 fix — without it the submission scores zero.

2. **Adapter raised on `None` observation.** `ObservationAdapter.parse` logged
   `obs.get(...)` before validating, so `parse(None)` raised `AttributeError`
   instead of `ObservationParseError`. Reordered validation before logging.
   (`agent/adapters/observation_adapter.py:22`; test
   `tests/unit/adapters/test_observation_adapter.py` now passes.)

## Notes / non-goals

- The learned layer (`HybridPolicy`/`LearnedPolicy`) remains a bounded, optional
  tie-breaker per the Stage 3 learning report; it degrades to the champion when
  no trained bundle is present and was included in the arena as a challenger.
- Economy re-tuning (crop mixes, pricing) is a Stage 1–3 concern; Stage 4 focused
  on horizon handling, robustness, selection, and submission engineering. The
  champion already outperforms `starter` locally.

## How to submit

```bash
tar -czf submission.tar.gz main.py agent
kaggle competitions submit kaggriculture -f submission.tar.gz -m "Stage 4 champion_endgame"
```

Verify first: `python -m mypy agent && python -m pytest tests && python -m agent.submission.submission_check`.
