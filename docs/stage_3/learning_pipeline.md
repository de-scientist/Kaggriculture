# Learning Pipeline (Stage 3)

The Stage 3 learning layer turns full Kaggriculture episodes into a
value + policy + OOD model bundle that the champion planner can optionally
consult. It is deliberately *advisory*: the hand-crafted champion remains the
decision maker, and any learned signal is applied only as a bounded
tie-breaker or distress signal. When no model is present or the state is
out-of-distribution, learned policies degrade to the champion exactly.

## Modules

| Module | Responsibility |
|---|---|
| `agent/learning/experience.py` | `ExperienceRecorder` — one JSON row per turn + `manifest.jsonl` |
| `agent/learning/dataset.py` | group rows into episodes, label (final bank / action type), episode-wise split, leak checks |
| `agent/learning/features.py` | versioned 58-feature encoder (`FEATURE_VERSION = 1`) — no future / private / engine info |
| `agent/learning/trainer.py` | `fit_and_register` — fit scaler, value, policy, OOD; save + register bundle |
| `agent/learning/model_registry.py` | `ModelRegistry` — versioned, statused entries in `manifest.json` |
| `agent/learning/registry.py` | runtime loader — `load_latest_bundle()`, placeholder on any failure |
| `agent/learning/models/bundle.py` | `LearnedBundle` — serialized model bundle, `is_ready()` gate |
| `agent/runtime/policies.py` | `LearnedPolicy` / `HybridPolicy` — bounded use of the bundle |

## Registry statuses

The registry (`artifacts/models/manifest.json`) tracks one entry per model:

| Status | Meaning |
|---|---|
| `experimental` | just trained, not yet validated |
| `validated` | passed offline evaluation on held-out episodes |
| `challenger` | validated, selected for champion/challenger A/B |
| `champion` | currently deployed bundle (runtime default when present) |
| `rejected` / `deprecated` | evaluated and dropped / superseded |

Only one entry may be `champion`; promoting a new champion automatically
deprecates the old one. The runtime loader (`registry.py`) picks
`registry.active()` — champion if present, else newest
validated/challenger.

## Pipeline

```bash
# 1. Collect experiences (per-turn rows) — 20 games by default
python scripts/stage3/collect_episodes.py \
    --seeds 1,2,3,4,5 --opponents random,pass,starter,champion \
    --out-dir experiments/stage3/experiences

# 2. Train + register (value ridge, policy logistic, OOD detector)
python scripts/stage3/train.py \
    --in-dir experiments/stage3/experiences \
    --model-dir artifacts/models --dataset-version d1 \
    --note "champion experiences"

# 3. Promote after offline evaluation
python -c "
from agent.learning.model_registry import ModelRegistry
ModelRegistry('artifacts/models').set_status('<model_id>', 'challenger')
"

# 4. A/B champion vs learned vs hybrid
python scripts/stage3/tournament.py --model-dir artifacts/models \
    --policies champion,hybrid,learned --games 8 --opponents random \
    --out-dir experiments/stage3/tournaments/r8
```

## Runtime integration

`agent/runtime/policies.py` exposes three policies with the same
`TurnPlanner` interface:

- `champion` — pure heuristic (`best_crop` + task ranking). Never changes.
- `learned` — champion plan, then: (1) a *sell-pressure* adjustment derived
  from the value model (only when the state is in-distribution), and (2)
  task re-ranking by `task.value + 25.0 * P(model action type)`.
- `hybrid` — like learned, but champion value is weighted 2× so the model
  can only resolve close calls, never overturn a clear champion decision.

Both learned policies skip all adjustments when the bundle is absent, not
ready, or the feature vector is flagged out-of-distribution (OOD
`mean-abs-z` distance > 2.25). `KAG_RUNTIME_MODEL_DIR` overrides the model
directory; `KAG_RUNTIME_RECORD_EXPERIENCE` toggles experience recording.

## Current result

See `reports/stage_3_learning_report.md`. The champion remains the deployed
strategy; `m1786489001-5be91f` is registered as `challenger`. Learned and
hybrid were statistically indistinguishable from champion (~±1% vs
`random`, identical vs `pass`/`starter`) with higher variance and no
consistent win, so no promotion was made.

## Notes

- Environment RNG is not fully seed-determined across processes, so
  tournament comparisons must be within-process (same script invocation).
- Models are refused at load when `feature_version` mismatches the current
  schema — retrain when features change.
- Artifacts (`artifacts/`) and experiments (`experiments/`) are
  git-ignored; the scripts and this doc are the source of truth.
