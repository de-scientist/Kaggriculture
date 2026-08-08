# Competition Constraints

## Runtime Environment

The official Kaggle competition runtime provides:

- **Python:** 3.11+ (Kaggle uses recent CPython)
- **kaggle-environments:** Latest released version
- **Standard library:** Full Python standard library
- **Third-party packages:** Only what's pre-installed by Kaggle

## Restricted Operations

The following are **not available** in the competition runtime:

- Internet/network access (no HTTP requests, API calls)
- Filesystem writes outside /tmp (read-only submission package)
- Subprocesses or shell execution
- GPU/TPU access
- Threading/multiprocessing (single-threaded execution)

## Time Constraints

Each turn, the Kaggle environment gives the agent a time budget. The
official default is generous (typically minutes), but practical agents
should complete decisions in under 500 ms to avoid timeouts in batch
scenarios.

## Memory Constraints

The Kaggle runtime has finite memory. The agent should use less than
512 MB for a typical episode.

## Submission Requirements

### Required Files

```
main.py          # Entry point with agent function
agent/           # Agent package (or all code in main.py for single-file)
```

### Prohibited Content

- Local absolute paths
- Developer usernames or home directories
- Private credentials or API keys
- Untracked files or uncommitted source
- IDE configuration files

## Dependency Constraints

The submission should only depend on:

- `kaggle-environments` (provided by the runtime)
- `pyyaml` (if used for config)
- Standard library

Development dependencies (`ruff`, `mypy`, `pytest`, `mkdocs`) are NOT
available in the competition runtime and must not be imported at runtime.

## Action Validation

Kaggle silently ignores invalid actions. The agent must:

- Only submit valid operations
- Only move within bounds
- Only plant with available seeds
- Only harvest mature crops
- Only sell items in shed
- Only buy what it can afford

Invalid actions are silent no-ops but waste the turn.
