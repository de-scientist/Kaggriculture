FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "agent.agent"]