class KaggricultureAIError(Exception):
    def __init__(self, message: str, details: Any = None):
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class InvalidObservationError(KaggricultureAIError):
    pass


class IllegalActionError(KaggricultureAIError):
    pass


class ConfigError(KaggricultureAIError):
    pass


class SimulationError(KaggricultureAIError):
    pass


class BudgetExceededError(KaggricultureAIError):
    pass