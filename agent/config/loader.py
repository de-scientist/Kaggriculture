import yaml
from pathlib import Path
from agent.config import settings


DEFAULT_CONFIG_DIR = Path(__file__).parent.parent.parent / "configs"


def load_config(name: str = "development") -> settings.Settings:
    path = DEFAULT_CONFIG_DIR / f"{name}.yaml"
    if not path.exists():
        raise ConfigurationError(f"Config file not found: {path}")
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return settings.Settings(**data)


def get_config() -> settings.Settings:
    return load_config("development")