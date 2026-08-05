from agent.exceptions.base import KaggricultureError


class AdapterError(KaggricultureError):
    pass


class ObservationParseError(AdapterError):
    pass


class MissingFieldError(AdapterError):
    pass


class InvalidCoordinateError(AdapterError):
    pass


class UnknownActionError(AdapterError):
    pass


class SchemaValidationError(AdapterError):
    pass


class SerializationError(AdapterError):
    pass


class CompatibilityError(AdapterError):
    pass
