# Stage 3 Learning Report

## Metadata

| Field | Value |
|---|---|
| Stage | 3 (offline learning + champion/challenger evaluation) |
| Commit | `0082417` |
| Dataset Version | `d1` |
| Challenger Model | `m1786489001-5be91f` |
| Champion Policy | `agent/runtime/policies.py` — `ChampionPolicy` |
| Entry Point | `agent/agent.py` → `agent(obs)` |
| Run Time | ~14 min (collection 269 s + training 11 s + tournaments 553 s) |

## Executive Summary

**Decision: keep the hand-crafted champion.** Two learned policies
(`learned`, `hybrid`) built on top of the champion planner were trained on
20 champion-played episodes and evaluated in full 720-turn tournaments.
On a 3-game round against all built-in opponents the learned policy was
indistinguishable from the champion (~±1%), and on a higher-powered 8-game
round against `random` both learned variants showed higher variance and no
consistent win. The challenger model remains registered in
`artifacts/models/manifest.json` (status `challenger`) for future
experiments; it degrades to the champion exactly when no model is present.

## Pipeline Overview

```
collect_episodes.py ─▶ experiences/*.jsonl (per-turn rows + manifest)
        │
        ▼
train.py (fit_and_register)
        │  episode-level split → scaler → value model
        │                       → policy model → OOD detector
        ▼
model_registry (register as experimental)
        │
        ▼
promote → challenger (set_status)
        │
        ▼
tournament.py (champion vs hybrid vs learned vs opponents)
```

All stages are reproducible with the scripts in `scripts/stage3/` (see
[Reproduction](#reproduction)).

## Episode Collection

Run: `python scripts/stage3/collect_episodes.py --seeds 1,2,3,4,5
--opponents random,pass,starter,champion` — 20 full episodes (720 turns),
4 opponents × 5 seeds, policy = champion, recorded via
`agent/learning/experience.py::ExperienceRecorder` (one JSON row per turn,
plus a `manifest.jsonl` of episode metadata).

| Opponent | Seeds | Champion p0 reward (min / max) | Notes |
|---|---|---|---|
| random | 1–5 | 15,114 / 23,646 | weakest, highest spread |
| pass | 1–5 | 22,364 / 23,659 | deterministic baseline |
| starter | 1–5 | 21,962 / 23,514 | weak opponent |
| champion (self-play) | 1–5 | 11,681 / 14,659 | perfect ties both sides |

Total rows recorded: 20 episodes × 720 turns ≈ 14,400 (per-player).

## Dataset

Build: `agent/learning/dataset.py` — groups JSONL rows into episodes, joins
manifest metadata, labels each row with the episode's final bank (value
target `final_money`) and the farmer action type actually chosen (policy
target), and splits **episode-wise** (no episode appears in more than one
split, enforced by `validate_no_leakage`).

| Field | Value |
|---|---|
| Dataset version | `d1` |
| Train episodes / rows | 20 / 14,380 |
| Val episodes / rows | 4 / 2,876 |
| Test episodes / rows | 5 / 3,595 |
| Feature version | 1 (58 features, `build_features`) |
| Policy classes | 6 (`water`, `harvest`, `plant`, `dig`, `pass`, `water_bonus`) |

Train class distribution: `water` 4144, `harvest` 3772, `plant` 3349,
`dig` 1377, `water_bonus` 765, `pass` 973.

## Model Training

Run: `python scripts/stage3/train.py --in-dir experiments/stage3/experiences
--model-dir artifacts/models --dataset-version d1 --note "champion
experiences: 20 games vs random/pass/starter/self-play"` (wraps
`agent/learning/trainer.py::fit_and_register`, seed 0).

| Model | Specification | Hold-out metrics |
|---|---|---|
| Value | ridge regression (alpha 1.0) on `final_money` | test RMSE 1403, test R² 0.894, test MAE 1085 |
| Policy | multinomial logistic over 6 action types (400 epochs, lr 0.5, reg 1e-4) | test acc 0.480, val acc 0.479, mean confidence 0.423 |
| OOD | mean-abs-z distance (train distance 0.615, threshold 2.25) | — |

Value train R² 0.931 / val R² 0.852; policy train acc 0.472. Train time
10.7 s. Full metrics in `artifacts/models/manifest.json` and the model card
(`artifacts/models/m1786489001-5be91f/model_card.md`).

**Caveat:** the policy accuracy (~0.48) is well above the ~0.29 majority
baseline but far from the champion's own consistency — the policy layer is
treated as a *tie-breaker / distress signal* only, never as the primary
decision maker (see `agent/runtime/policies.py`).

## Registry & Promotion

`agent/learning/model_registry.py::ModelRegistry` manages
`artifacts/models/manifest.json`. Two models are registered:

| Model ID | Status | Dataset | Note |
|---|---|---|---|
| `m1786485429-98dac4` | experimental | d-smoke | smoke test, 2 train episodes |
| `m1786489001-5be91f` | **challenger** | d1 | champion experiences, 20 games |

The d1 model was promoted with
`ModelRegistry.set_status("m1786489001-5be91f", "challenger")` after offline
evaluation. No model is marked `champion`, so the runtime default remains the
pure heuristic champion and every learned policy falls back to it when the
bundle is absent or out-of-distribution.

## Tournament

Run: `python scripts/stage3/tournament.py --model-dir artifacts/models
--policies champion,hybrid,learned --games 3 --out-dir
experiments/stage3/tournaments` and an 8-game focused round vs `random`
(`--games 8 --opponents random`). Reported value = final bank delta
(mean reward of games).

### Round 1 — 3 games × all opponents

| Pairing | Mean delta | Rewards |
|---|---|---|
| champion vs random | 23,186 | 22642, 22561, 24355 |
| champion vs pass | 20,027 | 19839, 19582, 20659 |
| champion vs starter | 19,271 | 19365, 18967, 19481 |
| hybrid vs random | 20,968 | 17059, 23154, 22690 |
| hybrid vs pass | 20,027 | 19839, 19582, 20659 |
| hybrid vs starter | 19,271 | 19365, 18967, 19481 |
| learned vs random | 23,432 | 23483, 22752, 24060 |
| learned vs pass | 20,027 | 19839, 19582, 20659 |
| learned vs starter | 19,271 | 19365, 18967, 19481 |

### Round 2 — 8 games vs `random` (discriminating pairing)

| Pairing | Mean | Min | Max |
|---|---|---|---|
| champion vs random | 22,755 | 16,504 | 24,127 |
| learned vs random | 21,877 | 16,677 | 25,134 |
| hybrid vs random | 22,216 | 15,190 | 23,701 |

## Analysis

- **vs passive opponents (pass/starter)** the champion, hybrid, and learned
  policies produced *identical* rewards on identical seeds — the learned
  adjustments never changed the outcome, and per-run RNG variation is the
  only noise. This makes `random` the discriminating opponent.
- **vs random**, learned beat champion in round 1 (23,432 vs 23,186) but
  lost in the 8-game round (21,877 vs 22,755); hybrid was worse in both.
  Both learned variants have larger min/max spread than the champion —
  i.e. higher variance with no consistent edge.
- **Environment RNG is not fully seed-determined across processes**: the
  `random` opponent behaves differently per process even at equal seeds, so
  only within-process comparisons are valid (hence the round 1 / round 2
  disagreement). This raises the bar for any future A/B to a paired,
  same-process design.

## Decision

Keep `ChampionPolicy` as the deployed strategy; do not promote the learned
bundle. The challenger stays in the registry (status `challenger`) so the
pipeline and runtime integration remain testable, and so a future, larger
dataset can be compared against these numbers. The learned layer is wired in
(`agent/runtime/policies.py` — `LearnedPolicy` / `HybridPolicy`) and will
activate only if a model with a clear, consistent win is ever registered.

## Known Limitations

1. Dataset is small (20 train episodes, one policy, 4 opponents).
2. Policy accuracy (~0.48) limits the learned layer to tie-breaking; it is
   deliberately bounded (`rank_weight` 25.0, hybrid weights champion value
   at 2×).
3. Cross-process seed non-determinism weakens tournament signal; paired
   within-process A/B is required for confident comparisons.
4. Only farmer action *type* is modeled; planting-time, movement, and market
   decisions remain entirely heuristic.

## Reproduction

```bash
# 1. Collect episodes (20 games)
python scripts/stage3/collect_episodes.py --seeds 1,2,3,4,5 \
    --opponents random,pass,starter,champion

# 2. Train + register (writes artifacts/models/m*/model.json + manifest)
python scripts/stage3/train.py --in-dir experiments/stage3/experiences \
    --model-dir artifacts/models --dataset-version d1 \
    --note "champion experiences: 20 games vs random/pass/starter/self-play"

# 3. Promote challenger
python -c "
from agent.learning.model_registry import ModelRegistry
ModelRegistry('artifacts/models').set_status('<model_id>', 'challenger')
"

# 4. Tournament
python scripts/stage3/tournament.py --model-dir artifacts/models \
    --policies champion,hybrid,learned --games 3 \
    --out-dir experiments/stage3/tournaments
```

Artifacts and experiment outputs are git-ignored (`artifacts/`,
`experiments/`); the report's numbers are reproducible from the scripts.
