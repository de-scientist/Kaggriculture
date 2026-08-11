"""Stage 3 learning layer.

The package implements the offline, evidence-driven learning system that wraps
the Stage 2 champion (``agent.runtime``):

* :mod:`agent.learning.features` — versioned state features for learning.
* :mod:`agent.learning.experience` — per-turn experience collection.
* :mod:`agent.learning.replay_buffer` — bounded, prioritized replay storage.
* :mod:`agent.learning.models` — tiny, pure-Python models used at runtime.
* :mod:`agent.learning.dataset` — episode-split datasets with leakage checks.
* :mod:`agent.learning.trainer` — offline training pipeline.
* :mod:`agent.learning.model_registry` — versioned model registry.
* :mod:`agent.learning.registry` — runtime bundle loader.

The runtime never imports numpy/sklearn; models are serialized to plain JSON
and inferred with pure Python so the competition runtime stays dependency-free.
"""

from __future__ import annotations

from .bundle import LearnedBundle
from .experience import ExperienceRecorder
from .features import FEATURE_VERSION, build_features
from .registry import load_latest_bundle

__all__ = [
    "FEATURE_VERSION",
    "ExperienceRecorder",
    "LearnedBundle",
    "build_features",
    "load_latest_bundle",
]
