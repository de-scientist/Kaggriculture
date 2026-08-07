from agent.exceptions.base import KaggricultureError


class ConfigurationError(KaggricultureError):
    """Raised when configuration is missing, invalid, or inconsistent."""
