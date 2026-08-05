# Deployment

## Local Development

```bash
# Install dependencies
pip install -e .

# Run the agent locally
python -m agent.agent

# Run with Docker
docker build -t kaggriculture-ai .
docker run -v $(pwd)/configs:/app/configs kaggriculture-ai
```

## Docker Compose

```bash
# Development
docker-compose up agent

# Run tests
docker-compose up test

# Run linter
docker-compose up lint
```

## CI/CD

GitHub Actions workflows are defined in `.github/workflows/`:

- `ci.yml` — formatting and linting
- `tests.yml` — unit and integration tests
- `lint.yml` — code quality checks
- `release.yml` — automated releases

## Kaggle Submission

```bash
# Single file
kaggle competitions submit kaggriculture -f main.py -m "v1"

# Multi-file bundle
tar -czf submission.tar.gz main.py helper.py
kaggle competitions submit kaggriculture -f submission.tar.gz -m "v1"
```

## Monitoring

- Prometheus metrics are exposed on port 9090 (optional).
- Logs are written to `logs/` directory.
- Experiment results are stored in `experiments/`.