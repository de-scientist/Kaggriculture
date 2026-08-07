"""Base exception for the Kaggriculture AI platform.

All domain-specific exceptions derive from :class:`KaggricultureError` so that
call-sites can catch every platform error with a single ``except`` clause
while still distinguishing specific failure modes via subclasses.

Each exception captures an optional ``context`` dict carrying diagnostic
information (turn, day, player, component, etc.) to support structured
logging and replay analysis.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class KaggricultureError(Exception):
    """Root exception for all Kaggriculture AI errors.

    Attributes:
        context: Arbitrary diagnostic key/value pairs attached to the error
            (e.g. ``{"turn": 128, "day": 6, "player": 0}``).
    """

    def __init__(self, message: str = "", *, context: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self._context: dict[str, Any] = dict(context) if context else {}

    @property
    def context(self) -> dict[str, Any]:
        return dict(self._context)

    def with_context(self, **kwargs: Any) -> KaggricultureError:
        """Return a copy of this error enriched with extra context fields."""
        merged = {**self._context, **kwargs}
        new = self.__class__(self.message, context=merged)
        # Preserve chained traceback information.
        new.__cause__ = self.__cause__
        new.__context__ = self.__context__
        return new

    def __str__(self) -> str:
        if self._context:
            details = ", ".join(f"{k}={v!r}" for k, v in self._context.items())
            return f"{self.message} (context: {details})"
        return self.message
