"""Observability package: metrics, profiling, tracing, telemetry, replay,
performance-budget enforcement.

Public entry points are the module-level singletons:

* :func:`get_metrics`  — cumulative :class:`MetricsCollector`
* :func:`get_profiler` — :class:`Profiler` (disabled unless ``ENABLE_PROFILING``)
* :func:`get_tracer`   — :class:`Tracer` for decision traces
* :func:`get_telemetry`— :class:`Telemetry` aggregator
* :func:`get_replay_store` — :class:`ReplayStore`
"""

from agent.observability.metrics import (
    MetricsCollector,
    RateCounter,
    get_metrics,
    reset_metrics,
)
from agent.observability.performance import (
    BudgetResult,
    BudgetStatus,
    PerformanceBudget,
    PerformanceMonitor,
)
from agent.observability.profiler import (
    Profiler,
    ProfileSample,
    get_profiler,
    profile_scope,
    profiled,
    reset_profiler,
)
from agent.observability.profiler import (
    enable as enable_profiling,
)
from agent.observability.profiler import (
    is_enabled as profiling_enabled,
)
from agent.observability.replay import (
    ReplayRecord,
    ReplayStore,
    get_replay_store,
    reset_replay_store,
)
from agent.observability.telemetry import (
    Telemetry,
    TelemetrySnapshot,
    get_telemetry,
    reset_telemetry,
)
from agent.observability.tracing import (
    Span,
    Trace,
    Tracer,
    get_active_trace,
    get_default_tracer,
    make_correlation_id,
    make_decision_id,
    reset_default_tracer,
    set_active_trace,
    trace_scope,
)

__all__ = [
    "BudgetResult",
    "BudgetStatus",
    "MetricsCollector",
    "PerformanceBudget",
    "PerformanceMonitor",
    "ProfileSample",
    "Profiler",
    "RateCounter",
    "ReplayRecord",
    "ReplayStore",
    "Span",
    "Telemetry",
    "TelemetrySnapshot",
    "Trace",
    "Tracer",
    "enable_profiling",
    "get_active_trace",
    "get_default_tracer",
    "get_metrics",
    "get_profiler",
    "get_replay_store",
    "get_telemetry",
    "make_correlation_id",
    "make_decision_id",
    "profile_scope",
    "profiled",
    "profiling_enabled",
    "reset_default_tracer",
    "reset_metrics",
    "reset_profiler",
    "reset_replay_store",
    "reset_telemetry",
    "set_active_trace",
    "trace_scope",
]
