from typing import Dict, Any


class ConfigSchema:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value