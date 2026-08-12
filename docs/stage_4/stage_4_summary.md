# Stage 4 Summary — Championship Optimization & Submission Engineering

Stage 4 hardens the validated Stage 1–3 components into a submission-ready
champion and proves it is competition-compliant.

## What was built

1. **Endgame optimization** (`agent/runtime/policies.py:56` `EndgamePolicy`).
   The submission champion now switches strategy by horizon: normal growth for
   days 0–21, wind-down (stop land/animals, taper hiring) for days 22–25, and
   full liquidation (stop planting, sell the shed) from day 26. Early-game
   behaviour is unchanged, so there is no regression risk.

2. **Champion / challenger arena** (`agent/submission/championship.py`).
   `ChampionArena` runs a round-robin over candidate policies using the Stage 3
   self-play framework and selects a champion with **champion protection** (a
   challenger only dethrones the incumbent on a clear average-reward margin).
   `default_candidates()` enumerates the pool; `select_champion_from_tournament`
   is the one-shot helper.

3. **Fail-safe hierarchy** (`agent/submission/failsafe.py`). `FailSafeAgent`
   wraps the submission entry point so a single turn can never crash the episode.
   It tolerates the Kaggle two-argument calling convention
   `agent(obs, configuration)`, repairs malformed action dicts via `legalize`,
   and returns `EMERGENCY_ACTION` on any exception. Wired into `main.py`.

4. **Submission compliance checker** (`agent/submission/submission_check.py`).
   Implements the §72 checklist programmatically: importable, callable, legal
   sample action, fail-safe present, and a full validation episode. `run_all()`
   regenerates `COMPETITION_COMPLIANCE_CHECKLIST.md`.

5. **Critical bug fix.** The submission agent previously raised `TypeError`
   under the Kaggle two-argument call and was marked `ERROR` every game (reward
   locked at the 3,000 starting money). The `FailSafeAgent` signature fix makes
   the agent actually play; local validation now shows ~20k coins and wins vs
   `random` and `starter`.

## Validation

| Matchup | Our coins | Status |
| --- | --- | --- |
| vs `random` | ~20,700 | DONE (win) |
| vs `starter` | ~20,000 | DONE (win) |
| self (mirror) | ~10,400 | DONE (tie) |

- `mypy` strict on `agent/`: clean (198 files).
- `pytest tests`: 718 prior + 19 new submission tests pass (one pre-existing
  adapter edge-case bug also fixed: `agent/adapters/observation_adapter.py:22`).

## Deliverables

- `STAGE_4_BASELINE_SELECTION.md`
- `FINAL_CHAMPION_SCORECARD.md`
- `FINAL_SUBMISSION_MANIFEST.md`
- `COMPETITION_COMPLIANCE_CHECKLIST.md`
- `STAGE_4_COMPLETION_REPORT.md`
- `docs/stage_4/` (this summary)
