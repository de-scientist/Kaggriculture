#!/usr/bin/env python3
"""Stage 3 — train a value + policy + OOD model bundle and register it.

Loads the raw experience episodes produced by ``collect_episodes.py``, splits
episode-wise, fits the scaler/value/policy/OOD models, saves the bundle under
``--model-dir``, and registers it in the model registry as ``experimental``.

Example::

    python scripts/stage3/train.py --in-dir experiments/stage3/experiences \\
        --model-dir artifacts/models --dataset-version d1 --note "champion bc1"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in-dir", default="experiments/stage3/dataset", type=str)
    parser.add_argument("--model-dir", default="artifacts/models", type=str)
    parser.add_argument("--dataset-version", default="", type=str)
    parser.add_argument("--seed", default=0, type=int)
    parser.add_argument("--value-alpha", default=1.0, type=float)
    parser.add_argument("--min-class-samples", default=5, type=int)
    parser.add_argument("--note", default="", type=str)
    args = parser.parse_args()

    from agent.learning.trainer import fit_and_register

    result = fit_and_register(
        experiences_dir=args.in_dir,
        model_dir=args.model_dir,
        dataset_version=args.dataset_version,
        seed=args.seed,
        value_alpha=args.value_alpha,
        min_class_samples=args.min_class_samples,
        note=args.note,
        registry_status="experimental",
    )
    m = result["metrics"]
    summary = {"model_id": result["model_id"], "bundle_dir": result["bundle_dir"]}
    print(json.dumps(summary, indent=2))
    keys = [
        "value_train_rmse",
        "value_val_rmse",
        "value_test_rmse",
        "value_test_r2",
        "policy_train_acc",
        "policy_val_acc",
        "policy_test_acc",
        "n_episodes_train",
        "n_episodes_val",
        "n_episodes_test",
    ]
    for key in keys:
        print(f"{key}: {m.get(key, 'n/a')}")
    print(f"policy classes: {m.get('policy_classes', [])}")


if __name__ == "__main__":
    main()
