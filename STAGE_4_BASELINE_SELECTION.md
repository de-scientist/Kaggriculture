# Stage 4 — Baseline Selection

**Goal.** Choose the submission candidate from the validated Stage 1–3
components, with champion protection, and document why.

## Candidate pool

All candidates share the production planner (`agent.runtime.planner`) and differ
only in their policy wrapper (`agent.runtime.policies`). The learned/hybrid
candidates degrade automatically to the champion when no trained bundle is
present, so every candidate is safe to ship.

| Candidate | Policy | Source | Notes |
| --- | --- | --- | --- |
| `champion_endgame` | `EndgamePolicy` (`auto`) | `agent/runtime/policies.py:56` | Championship hybrid: champion + horizon wind-down/liquidation |
| `hybrid` | `HybridPolicy` | `agent/runtime/policies.py:146` | Stage 3 bounded learned tie-breaker |
| `learned` | `LearnedPolicy` | `agent/runtime/policies.py:75` | Stage 3 value + policy signals |

The Stage 3 learning report (`reports/stage_3_learning_report.md`) concluded that
the hand-crafted champion should remain the primary submission and the learned
layer is a bounded tie-breaker. The endgame optimization
(`EndgamePolicy`, `agent/runtime/policies.py:56`) is the Stage 4 addition that
closes the horizon correctly (stop planting/land/animals, liquidate the shed).

## Selection method

`ChampionArena` (`agent/submission/championship.py`) runs a round-robin over the
candidates using the Stage 3 self-play framework
(`agent.evaluation.tournament`). Selection applies **champion protection**:
a challenger only dethrones the reigning champion when its average reward
exceeds the incumbent's by more than `win_margin` (default 0; i.e. an exact tie
keeps the champion). This prevents self-play noise from flipping the submission.

## Decision

`champion_endgame` (`EndgamePolicy`) is the selected submission champion.

Rationale:
- It is behaviourally identical to the champion for the first ~22 days, so no
  early-game regression risk.
- It adds the only missing Stage 4 behaviour (endgame liquidation) and is
  fully deterministic and model-free.
- It is the default policy produced by `make_policy("auto")`
  (`agent/runtime/policies.py:223`), so the submission surface (`main.py`) needs
  no special wiring beyond the fail-safe wrapper.

## Live validation (local `kaggle_environments`, 720-step episodes)

Executed via `python -m agent.submission.submission_check` and ad-hoc runs:

| Matchup | Our reward | Opponent | Status |
| --- | --- | --- | --- |
| champion_endgame vs `random` | ~20,700 | 0 | DONE (win) |
| champion_endgame vs `starter` | ~20,000 | ~3,300 | DONE (win) |
| champion_endgame vs champion_endgame | ~10,400 | ~10,500 | DONE (tie) |

Before the Stage 4 fail-safe fix the submission agent raised `TypeError` under
the Kaggle two-argument calling convention (`agent(obs, configuration)`) and was
marked `ERROR` every game (reward locked at the 3,000 starting money). The
`FailSafeAgent` wrapper now tolerates the two-argument convention
(`agent/submission/failsafe.py:54`), which is the single most important
submission-engineering fix of this stage.
