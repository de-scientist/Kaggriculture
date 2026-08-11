"""Schema and version constants for the Stage 3 learning layer.

Every persisted artifact (experience rows, datasets, models) carries explicit
version tags.  Consumers must refuse to combine incompatible versions rather
than silently misinterpreting data.
"""

from __future__ import annotations

# Bump whenever the experience row schema changes (fields/meaning).
EXPERIENCE_SCHEMA_VERSION = 1

# Bump whenever build_features changes (order, count, or meaning of features).
FEATURE_VERSION = 1

# Bump whenever the environment constants mirrored by the runtime change.
ENVIRONMENT_VERSION = "runtime-defaults-v1"

# Bump whenever the dataset builder changes labels or row semantics.
DATASET_SCHEMA_VERSION = 1

# Products/crops in stable order used everywhere in the learning layer.
CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
SALEABLE_PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL"]
ANIMALS = ["GOOSE", "COW", "SHEEP"]

# Action types the champion planner can emit for the main farmer.
ACTION_TYPES = ["plant", "harvest", "water", "water_bonus", "dig", "feed", "care", "collect", "place", "pass", "move"]
