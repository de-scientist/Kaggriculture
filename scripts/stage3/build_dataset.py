#!/usr/bin/env python3
"""Stage 3 — build the offline dataset from collected experience.

Loads all episodes under ``--in-dir``, verifies temporal leakage is impossible,
splits episode-wise into train/val/test, and writes a summary + a compact numpy
dataset artifact to ``--out-dir``.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.learning.dataset import (  # noqa: E402
    build_dataset,
    load_episodes,
    split_episodes,
    validate_no_leakage,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in-dir", default="experiments/stage3/experiences", type=str)
    parser.add_argument("--out-dir", default="experiments/stage3/dataset", type=str)
    parser.add_argument("--seed", default=0, type=int)
    parser.add_argument("--min-rows", default=720, type=int)
    args = parser.parse_args()

    episodes = load_episodes(args.in_dir)
    if not episodes:
        raise SystemExit(f"no episodes under {args.in_dir}")
    keep = [e for e in episodes if len(e.rows) >= args.min_rows]
    if len(keep) != len(episodes):
        print(f"dropped {len(episodes) - len(keep)} short/empty episodes")

    split = split_episodes(keep, seed=args.seed)
    violations = validate_no_leakage(split)
    if violations:
        raise SystemExit("leakage: " + "; ".join(violations))

    datasets = {name: build_dataset(group) for name, group in split.items()}
    summary = {
        "n_episodes": len(keep),
        "splits": {name: len(group) for name, group in split.items()},
        "rows": {name: len(ds) for name, ds in datasets.items()},
        "action_distribution": dict(
            sorted(
                Counter(
                    label for group in split.values() for ep in group for label in ep.policy_labels
                ).items()
            )
        ),
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "dataset_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Compact numpy artifacts consumed by train.py.
    import numpy as np

    for name, ds in datasets.items():
        np.save(out_dir / f"X_{name}.npy", np.asarray(ds.features, dtype=float))
        np.save(out_dir / f"y_value_{name}.npy", np.asarray(ds.value_labels, dtype=float))
        np.save(
            out_dir / f"y_policy_{name}.npy",
            np.asarray(ds.policy_labels, dtype=object),
            allow_pickle=True,
        )
        np.save(
            out_dir / f"episodes_{name}.npy",
            np.asarray(ds.episode_ids, dtype=object),
            allow_pickle=True,
        )

    print(json.dumps(summary, indent=2))
    print(f"wrote dataset artifacts to {out_dir}")


if __name__ == "__main__":
    main()
