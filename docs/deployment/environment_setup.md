# Environment Setup

## Runtime Requirements

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11+ | Tested on 3.13.14 |
| kaggle-environments | 1.0.0+ | Official Kaggle SDK |
| pyyaml | 6.0+ | YAML config parsing |
| ruff | 0.7.0+ | Linting |
| black | 24.0+ | Formatting |
| mypy | 1.10+ | Type checking |
| pytest | 8.0+ | Testing |
| pytest-cov | 5.0+ | Coverage |

## Operating-System Assumptions

- **Windows** (development): PowerShell 5.1
- **Linux** (CI/competition): Python 3.11+
- The agent itself is platform-agnostic (pure Python).

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `KAG_ENV` | `development` | Active configuration profile |
| `KAG_AGENT_SEED` | `42` | Random seed |
| `KAG_AGENT_STRATEGY` | `baseline` | Strategy name |
| `KAG_LOG_LEVEL` | `INFO` | Log level |
| `KAG_LOG_FORMAT` | `json` | Log format |
| `KAG_ENABLE_TRACING` | `true` | Enable tracing |
| `KAG_ENABLE_TELEMETRY` | `true` | Enable telemetry |
| `KAG_ENABLE_REPLAY` | `true` | Enable replay recording |

## Kaggle CLI (for submission)

```bash
pip install kaggle

# Set up credentials
mkdir -p ~/.kaggle
# Save API token to ~/.kaggle/access_token
chmod 600 ~/.kaggle/access_token
```

## Lockfile

The project uses `uv.lock` for dependency pinning. To ensure exact
reproducibility:

```bash
uv sync --frozen
```

## Docker (Optional)

A `Dockerfile` is available for containerized testing:

```bash
docker build -t kaggriculture-agent .
docker run kaggriculture-agent python scripts/validate_submission.py
```
