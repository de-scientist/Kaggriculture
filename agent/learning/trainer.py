"""Offline model training pipeline (numpy only; never runs in the episode).

Fits a value model (ridge regression on standardized features), a policy
model (multinomial logistic regression), and an OOD detector, then packages
them into a versioned :class:`LearnedBundle` and registers it in the model
registry.  The runtime only ever *loads* the bundle (pure Python).
"""

from __future__ import annotations

import time
import uuid
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from .dataset import (
    EpisodeDataset,
    build_dataset,
    split_episodes,
    validate_no_leakage,
)
from .features import FEATURE_NAMES, FEATURE_VERSION, NUM_FEATURES
from .model_registry import ModelRegistry
from .models.bundle import LearnedBundle, env_signature
from .models.ood import OODDetector
from .models.policy_model import SoftmaxPolicyModel
from .models.scaler import FeatureScaler
from .models.value_model import LinearValueModel
from .schema import ENVIRONMENT_VERSION


def _matrices(dataset: EpisodeDataset) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    features = np.asarray(dataset.features, dtype=float)
    values = np.asarray(dataset.value_labels, dtype=float)
    labels = np.asarray(dataset.policy_labels, dtype=object)
    return features, values, labels


def fit_value_model(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    alpha: float = 1.0,
) -> tuple[LinearValueModel, dict[str, float]]:
    """Ridge regression on standardized features."""
    _, f = x_train.shape
    xtx = x_train.T @ x_train + alpha * np.eye(f)
    xty = x_train.T @ y_train
    try:
        w = np.linalg.solve(xtx, xty)
    except np.linalg.LinAlgError:  # pragma: no cover - singular matrix
        w = np.linalg.lstsq(xtx, xty, rcond=None)[0]
    b = float(np.mean(y_train) - np.mean(x_train, axis=0) @ w)
    model = LinearValueModel(weights=[float(v) for v in w], bias=b)

    pred_train = x_train @ w + b
    pred_val = x_val @ w + b
    return model, {
        "value_train_rmse": _rmse(pred_train, y_train),
        "value_val_rmse": _rmse(pred_val, y_val),
        "value_train_r2": _r2(pred_train, y_train),
        "value_val_r2": _r2(pred_val, y_val),
        "value_train_mae": _mae(pred_train, y_train),
        "value_val_mae": _mae(pred_val, y_val),
        "value_alpha": alpha,
    }


def fit_policy_model(
    x_train: np.ndarray,
    labels_train: np.ndarray,
    x_val: np.ndarray,
    labels_val: np.ndarray,
    classes: Sequence[str],
    lr: float = 0.5,
    epochs: int = 400,
    reg: float = 1e-4,
    seed: int = 0,
    patience: int = 40,
) -> tuple[SoftmaxPolicyModel, dict[str, float]]:
    """Multinomial logistic regression via full-batch gradient descent."""
    rng = np.random.default_rng(seed)
    n, f = x_train.shape
    c = len(classes)
    index = {cls: i for i, cls in enumerate(classes)}
    onehot = np.zeros((n, c))
    counts = np.zeros(c)
    for i, label in enumerate(labels_train):
        idx = index.get(str(label))
        if idx is not None:
            onehot[i, idx] = 1.0
            counts[idx] += 1.0

    inv_freq = np.ones(c)
    for i in range(c):
        if counts[i] > 0:
            inv_freq[i] = float(n) / (c * counts[i])
    inv_freq = inv_freq / inv_freq.mean()

    weights = rng.normal(0.0, 1e-2, size=(c, f))
    bias = np.zeros(c)
    best_val = -1.0
    best_weights = weights.copy()
    best_bias = bias.copy()
    best_step = 0

    def accuracy(ww: np.ndarray, bb: np.ndarray, xx: np.ndarray, lab: np.ndarray) -> float:
        logits = xx @ ww.T + bb
        pred = np.argmax(logits, axis=1)
        correct = sum(1 for p, labv in zip(pred, lab, strict=True) if classes[p] == str(labv))
        return correct / len(lab) if len(lab) else 0.0

    val_acc = accuracy(weights, bias, x_val, labels_val)
    best_val = val_acc
    stale = 0
    for step in range(epochs):
        logits = x_train @ weights.T + bias
        exp = np.exp(logits - logits.max(axis=1, keepdims=True))
        probs = exp / exp.sum(axis=1, keepdims=True)
        grad = (probs - onehot) * inv_freq[None, :]
        grad_w = (grad.T @ x_train) / n + reg * weights
        grad_b = grad.sum(axis=0) / n
        weights -= lr * grad_w
        bias -= lr * grad_b
        if (step + 1) % 5 == 0:
            val_acc = accuracy(weights, bias, x_val, labels_val)
            if val_acc > best_val:
                best_val = val_acc
                best_weights = weights.copy()
                best_bias = bias.copy()
                best_step = step
                stale = 0
            else:
                stale += 1
                if stale >= patience:
                    break

    model = SoftmaxPolicyModel(
        classes=list(classes),
        weights=[[float(v) for v in row] for row in best_weights],
        bias=[float(v) for v in best_bias],
    )
    train_acc = accuracy(best_weights, best_bias, x_train, labels_train)
    return model, {
        "policy_train_acc": float(train_acc),
        "policy_val_acc": float(best_val),
        "policy_best_step": int(best_step),
        "policy_lr": lr,
        "policy_reg": reg,
        "policy_epochs": int(epochs),
    }


def fit_and_register(
    experiences_dir: str | Path,
    model_dir: str | Path,
    dataset_version: str = "",
    seed: int = 0,
    value_alpha: float = 1.0,
    min_class_samples: int = 5,
    note: str = "",
    registry_status: str = "experimental",
) -> dict[str, Any]:
    """End-to-end train: load experiences -> split -> fit -> register.

    Returns a summary dict with the model id and all metrics.
    """
    from .dataset import load_episodes

    start = time.time()
    episodes = load_episodes(experiences_dir)
    if not episodes:
        raise ValueError(f"no episodes found under {experiences_dir}")

    split = split_episodes(episodes, seed=seed)
    violations = validate_no_leakage(split)
    if violations:
        raise RuntimeError("dataset leakage detected: " + "; ".join(violations))

    datasets = {name: build_dataset(group) for name, group in split.items()}
    train_ds, val_ds, test_ds = datasets["train"], datasets["val"], datasets["test"]
    if len(train_ds) == 0:
        raise ValueError("empty training split")

    x_train, y_train, labels_train = _matrices(train_ds)
    x_val, y_val, labels_val = _matrices(val_ds)
    if len(val_ds) == 0:
        # No held-out episodes available (tiny collection); report in-sample.
        x_val, y_val, labels_val = x_train.copy(), y_train.copy(), labels_train.copy()

    scaler = FeatureScaler().fit(x_train.tolist())

    xs_train = np.asarray([scaler.transform(row) for row in x_train.tolist()], dtype=float)
    xs_val = np.asarray([scaler.transform(row) for row in x_val.tolist()], dtype=float)

    value_model, value_metrics = fit_value_model(
        xs_train, y_train, xs_val, y_val, alpha=value_alpha
    )

    class_counts = Counter(str(label) for label in labels_train)
    classes = [c for c, n in class_counts.most_common() if n >= min_class_samples]
    policy_model, policy_metrics = fit_policy_model(
        xs_train, labels_train, xs_val, labels_val, classes=classes, seed=seed
    )

    ood = OODDetector().fit(x_train.tolist())

    model_id = f"m{int(time.time())}-{uuid.uuid4().hex[:6]}"
    root = Path(model_dir)
    root.mkdir(parents=True, exist_ok=True)
    bundle_dir = root / model_id
    bundle_dir.mkdir(parents=True, exist_ok=True)

    test_metrics = _evaluate_test(value_model, policy_model, scaler, test_ds)

    bundle = LearnedBundle(
        value=value_model,
        policy=policy_model,
        scaler=scaler,
        ood=ood,
        feature_version=FEATURE_VERSION,
        feature_names=list(FEATURE_NAMES),
        model_id=model_id,
        metadata={
            "dataset_version": dataset_version,
            "environment_version": ENVIRONMENT_VERSION,
            "environment_signature": env_signature(),
            "n_features": NUM_FEATURES,
            "trained_at": time.time(),
            "seed": seed,
            "note": note,
        },
    )
    bundle.save(str(bundle_dir / "model.json"))

    metrics = {
        **value_metrics,
        **policy_metrics,
        **test_metrics,
        "dataset_version": dataset_version,
        "n_episodes_train": len(split["train"]),
        "n_episodes_val": len(split["val"]),
        "n_episodes_test": len(split["test"]),
        "n_rows_train": len(train_ds),
        "n_rows_val": len(val_ds),
        "n_rows_test": len(test_ds),
        "policy_classes": classes,
        "class_distribution_train": {k: v for k, v in sorted(class_counts.items())},
        "train_time_s": round(time.time() - start, 2),
        "ood_train_distance": ood.train_distance,
        "feature_version": FEATURE_VERSION,
        "seed": seed,
    }

    registry = ModelRegistry(root)
    registry.register(
        model_id=model_id,
        status=registry_status,
        feature_version=FEATURE_VERSION,
        dataset_version=dataset_version,
        metrics=metrics,
        note=note,
    )

    _write_model_card(bundle_dir, bundle, metrics)
    return {"model_id": model_id, "metrics": metrics, "bundle_dir": str(bundle_dir)}


def _evaluate_test(
    value_model: LinearValueModel,
    policy_model: SoftmaxPolicyModel,
    scaler: FeatureScaler,
    test_ds: EpisodeDataset,
) -> dict[str, float]:
    x_test = np.asarray(test_ds.features, dtype=float)
    y_test = np.asarray(test_ds.value_labels, dtype=float)
    labels_test = np.asarray(test_ds.policy_labels, dtype=object)
    xs_test = np.asarray([scaler.transform(row) for row in x_test.tolist()], dtype=float)

    pred = xs_test @ np.asarray(value_model.weights) + value_model.bias
    pred = np.asarray(pred, dtype=float)
    metrics: dict[str, float] = {
        "value_test_rmse": _rmse(pred, y_test),
        "value_test_r2": _r2(pred, y_test),
        "value_test_mae": _mae(pred, y_test),
    }

    if policy_model.n_classes:
        logits = xs_test @ np.asarray(policy_model.weights).T + np.asarray(policy_model.bias)
        pred_classes = np.argmax(logits, axis=1)
        correct = sum(
            1
            for p, labv in zip(pred_classes, labels_test, strict=True)
            if policy_model.classes[p] == str(labv)
        )
        metrics["policy_test_acc"] = correct / len(labels_test) if len(labels_test) else 0.0
        # Calibration: predicted prob of the chosen class vs empirical freq.
        exp = np.exp(logits - logits.max(axis=1, keepdims=True))
        probs = exp / exp.sum(axis=1, keepdims=True)
        chosen = probs[np.arange(len(labels_test)), pred_classes]
        metrics["policy_test_mean_confidence"] = float(chosen.mean()) if len(chosen) else 0.0
    return metrics


def _rmse(pred: np.ndarray, actual: np.ndarray) -> float:
    return float(np.sqrt(np.mean((pred - actual) ** 2))) if len(actual) else 0.0


def _mae(pred: np.ndarray, actual: np.ndarray) -> float:
    return float(np.mean(np.abs(pred - actual))) if len(actual) else 0.0


def _r2(pred: np.ndarray, actual: np.ndarray) -> float:
    if len(actual) == 0:
        return 0.0
    ss_res = float(np.sum((actual - pred) ** 2))
    ss_tot = float(np.sum((actual - np.mean(actual)) ** 2))
    if ss_tot == 0:
        return 0.0
    return 1.0 - ss_res / ss_tot


def _write_model_card(bundle_dir: Path, bundle: LearnedBundle, metrics: Mapping[str, Any]) -> None:
    n_features = bundle.scaler.n_features if bundle.scaler else 0
    preview = ", ".join(bundle.feature_names[:6])
    value_line = (
        f"- **Value model:** ridge regression (bias={bundle.value.bias:.3f})"
        if bundle.value is not None
        else "- **Value model:** none"
    )
    policy_line = (
        f"- **Policy model:** multinomial logistic over {len(bundle.action_types)} action types"
        if bundle.policy is not None
        else "- **Policy model:** none"
    )
    ood_line = (
        f"- **OOD detector:** mean-abs-z distance (train distance {bundle.ood.train_distance:.3f})"
        if bundle.ood is not None
        else "- **OOD detector:** none"
    )
    lines = [
        "# Model Card",
        "",
        f"- **Model ID:** `{bundle.model_id}`",
        f"- **Feature version:** {bundle.feature_version}",
        f"- **Environment version:** {ENVIRONMENT_VERSION}",
        f"- **Dataset version:** {metrics.get('dataset_version', '')}",
        f"- **Features:** {n_features} ({preview}, ...)",
        value_line,
        policy_line,
        ood_line,
        "",
        "## Metrics",
        "",
    ]
    for key, value in sorted(metrics.items()):
        skip_keys = ("policy_classes", "class_distribution_train")
        if isinstance(value, (int, float)) and key not in skip_keys:
            lines.append(f"- **{key}:** {value:.4g}")
    limitation = "- Predictions are only valid on states near the training distribution."
    lines.extend(["", "## Limitations", "", limitation, ""])
    (bundle_dir / "model_card.md").write_text("\n".join(lines), encoding="utf-8")
