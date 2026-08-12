# Final Submission Manifest

This document records exactly what is submitted for the Kaggriculture competition
and how to produce it.

## Submission shape

The Kaggle submission requires `main.py` at the package root exporting `agent`.
Everything is import-only at runtime — no training, no network, no external
state.

## Files included in the submission

| File | Role |
| --- | --- |
| `main.py` | Submission surface; `agent` = `FailSafeAgent(runtime_agent)` |
| `agent/runtime/agent.py` | `agent(obs)` entry; builds `GameSnapshot`, plans, returns action |
| `agent/runtime/planner.py` | Turn planner (tasks → unit assignment → ops) |
| `agent/runtime/policies.py` | `EndgamePolicy` (submission champion) + learned/hybrid |
| `agent/runtime/settings.py` | `RuntimeSettings` (frozen, env-overridable knobs) |
| `agent/runtime/{game,tasks,market,crops,paths,constants}.py` | Planner support |
| `agent/submission/failsafe.py` | Fail-safe hierarchy + emergency fallback |
| `agent/submission/championship.py` | Champion/challenger arena (offline selection) |
| `agent/submission/submission_check.py` | Compliance checklist (§72) |
| `agent/adapters/*`, `agent/domain/*`, `agent/config/*` | Observation/action adapters, domain model |
| `agent/decision/*`, `agent/strategies/*` | Decision engine + strategy registry |
| `agent/learning/*`, `agent/evaluation/*` | Optional learned layer + tournament (degrade safely) |

## How to submit

Single-file (the runtime is self-contained under `agent/`):

```bash
kaggle competitions submit kaggriculture -f main.py -m "Stage 4 champion_endgame"
```

Multi-file (recommended — bundles the whole `agent/` package):

```bash
tar -czf submission.tar.gz main.py agent
kaggle competitions submit kaggriculture -f submission.tar.gz -m "Stage 4 champion_endgame"
```

## Pre-submission verification

Run locally before every submit:

```bash
python -m mypy agent
python -m pytest tests
python -m agent.submission.submission_check
```

All three must be green. The checker regenerates
`COMPETITION_COMPLIANCE_CHECKLIST.md`.

## Human actions required before submit (outside this repo)

- Accept the competition rules at
  <https://www.kaggle.com/competitions/kaggriculture> ("Join Competition").
- Ensure the Kaggle CLI is authenticated (`~/.kaggle/access_token` or `kaggle auth login`).
- Verify submission with `kaggle competitions submissions kaggriculture` and review
  a replay via `kaggle competitions replay <EPISODE_ID>`.
