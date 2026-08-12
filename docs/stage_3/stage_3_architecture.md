# Stage 3 Architecture

This document maps the target decision pipeline from the Stage 3 master prompt
(§106) onto the implemented modules. Stage 3 builds on the Stage 1 (reliable)
and Stage 2 (economic) systems and adds an **adaptive learning layer** that is
always subordinate to the proven champion.

## Target pipeline (§106)

```
GAME OBSERVATION
   → CANONICAL GAME STATE
   → FEATURE ENGINE
   ├─ LEARNED POLICY
   ├─ ECONOMIC PLANNER (Stage 2 champion)
   └─ OPPONENT MODEL
   → STRATEGY EVALUATOR
   → CONFIDENCE CHECK
   ├─ HIGH  → LEARNED POLICY
   └─ LOW   → DEEP PLANNING (champion)
   → ECONOMIC SANITY CHECK
   → RISK CONTROLLER
   → ACTION VALIDATOR
   → GAME ACTION
```

## Implemented mapping

| Stage 3 requirement | Module | Notes |
|---|---|---|
| Canonical game state | `agent/runtime/game.py` `GameSnapshot` | Stage 2 |
| Feature engine | `agent/learning/features.py` | 58 features, `FEATURE_VERSION=1`, no future/private/engine info |
| Learned policy (value) | `agent/learning/models/value_model.py` `LinearValueModel` | ridge regression, pure-Python |
| Learned policy (action) | `agent/learning/models/policy_model.py` `SoftmaxPolicyModel` | multinomial logistic, softmax |
| Out-of-distribution | `agent/learning/models/ood.py` `OODDetector` | mean-abs-z distance |
| Bundle + `is_ready()` gate | `agent/learning/models/bundle.py` `LearnedBundle` | version-checked, placeholder on failure |
| Runtime loader | `agent/learning/registry.py` `load_latest_bundle()` | champion fallback guaranteed |
| Experience collection | `agent/learning/experience.py` | per-turn rows + manifest |
| Replay buffer | `agent/learning/replay_buffer.py` | bounded, prioritized, reproducible |
| Dataset + labels | `agent/learning/dataset.py` | episode-wise split, leak checks |
| Training pipeline | `agent/learning/trainer.py` `fit_and_register` | scaler→value→policy→OOD→register |
| Model registry | `agent/learning/model_registry.py` | versioned, statused (`experimental`→`champion`) |
| **Strategy-level hybrid** | `agent/strategies/hybrid_strategy.py` `HybridStrategy` | blends champion + learned by confidence; **new in this phase** |
| Runtime hybrid/learned | `agent/runtime/policies.py` `HybridPolicy`/`LearnedPolicy` | bounded tie-breaker over champion |
| Strategy selection | `agent/strategies/strategy_manager.py` | now registers `"hybrid"` |
| Adaptive strategy | `agent/strategies/adaptive_strategy.py` | mode controller (growth/endgame/…) |
| Opponent model | `agent/competition/opponent_model.py` | learned from observable history |
| **Safe exploration** | `agent/learning/exploration.py` `ExplorationPolicy` | epsilon-greedy + uncertainty, budget/endgame/confidence guards; **new** |
| **Self-play / tournament** | `agent/evaluation/tournament.py` | injectable simulator; default Kaggle runner; **new** |
| Champion/challenger scripts | `scripts/stage3/{collect_episodes,train,tournament,build_dataset}.py` | end-to-end experiments |

## Decision flow in `HybridStrategy`

1. Always score candidates with the Stage 2 `EconomicStrategy` (champion).
2. Load the active bundle. Missing / `is_ready()==False` / feature error /
   inference error → **return champion scores unchanged**. Learning can never
   break play (non-negotiable rule, §4).
3. If the state is out-of-distribution (`OODDetector.is_ood`) or policy
   confidence `< confidence_threshold` → champion only.
4. Otherwise blend a softmax-normalized champion score with the learned
   policy's probability for each candidate's action type; blend weight scales
   with confidence (`learned_weight × confidence`).
5. Economic sanity guardrail: any candidate whose `estimated_cost` exceeds
   available capital is rejected (`score = -inf`).

The hybrid is registered as a selectable strategy (`"hybrid"`); it is not the
default so the Stage 2 champion remains active unless explicitly chosen. The
runtime `HybridPolicy` in `agent/runtime/policies.py` provides the older,
bounded tie-breaker variant.

## Safety invariants

* No future information in features (verified by `test_temporal_leakage.py`).
* No uncontrolled self-modification: models load from controlled artifacts only.
* Model rollback via registry status; placeholder bundle on any load failure.
* Invalid / OOD / low-confidence states degrade to the champion.
* Exploration only chooses among already-validated legal options and is bounded
  by budget, endgame horizon, and confidence.
