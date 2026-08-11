"""Runtime model loader used by ``agent.runtime.policies``.

The runtime never ships weights; it looks up the registry's active bundle and
loads it as a pure-Python :class:`LearnedBundle`.  Any failure (missing
registry, corrupt file, version mismatch) yields a placeholder bundle whose
``is_ready()`` is False, so the champion planner always remains the fallback.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from .model_registry import ModelRegistry
from .models.bundle import LearnedBundle

logger = logging.getLogger(__name__)

DEFAULT_MODEL_DIR = "artifacts/models"

_bundle_cache: LearnedBundle | None = None
_cache_key: tuple[str, str] | None = None


def default_model_dir() -> Path:
    raw = os.environ.get("KAG_RUNTIME_MODEL_DIR")
    return Path(raw) if raw else Path(DEFAULT_MODEL_DIR)


def active_bundle_path() -> Path | None:
    """Path to the active model.json, if any."""
    registry = ModelRegistry(default_model_dir())
    entry = registry.active()
    if entry is None:
        return None
    path = registry.bundle_path(entry.model_id)
    return path if path.exists() else None


def load_latest_bundle() -> Any:
    """Load the active bundle (cached).  Returns a placeholder on failure."""
    global _bundle_cache, _cache_key
    try:
        path = active_bundle_path()
        key = (str(path), str(path.stat().st_mtime) if path else "")
        if _bundle_cache is not None and _cache_key == key:
            return _bundle_cache
        if path is None:
            _bundle_cache = LearnedBundle.placeholder()
            _cache_key = key
            return _bundle_cache
        _bundle_cache = LearnedBundle.load(str(path))
        _cache_key = key
        if not _bundle_cache.is_ready():
            logger.warning("loaded bundle %s is not ready; using champion", path)
        return _bundle_cache
    except Exception:  # pragma: no cover - registry must never break play
        logger.exception("failed to load learned bundle; using champion")
        _bundle_cache = LearnedBundle.placeholder()
        _cache_key = None
        return _bundle_cache


def reset_bundle_cache() -> None:
    """Drop the cached bundle (used by tests and collection scripts)."""
    global _bundle_cache, _cache_key
    _bundle_cache = None
    _cache_key = None
