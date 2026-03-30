import operator
from typing import Annotated, Any, TypedDict


def _keep_last(current: Any, update: Any) -> Any:
    """Last writer wins — safe for input fields (query, bi_data, etc.) that are
    never mutated by agents and will always carry the same value across parallel writes."""
    return update


def _keep_nonempty(current: Any, update: Any) -> Any:
    """Keep the most recent non-empty value. Used for agent output fields so that a
    parallel agent returning an empty string never overwrites content written by the
    agent that owns that field."""
    return update if update else current


class AgentState(TypedDict):
    # Input from the user/trigger
    query:             Annotated[str,                      _keep_last]

    # Data context provided to the system
    bi_data:           Annotated[dict[str, Any],           _keep_last]
    media_data:        Annotated[dict[str, Any],           _keep_last]
    review_data:       Annotated[dict[str, Any],           _keep_last]
    forecast_data:     Annotated[dict[str, Any],           _keep_last]

    # Orchestrator routing
    next_agents:       Annotated[list[str],                _keep_last]
    routing_reasoning: Annotated[str,                      _keep_last]

    # Agent outputs — _keep_nonempty prevents parallel agents returning ""
    # from overwriting content written by the agent that owns each field
    bi_analysis:           Annotated[str,                  _keep_nonempty]
    media_analysis:        Annotated[str,                  _keep_nonempty]
    pricing_analysis:      Annotated[str,                  _keep_nonempty]
    reputation_analysis:   Annotated[str,                  _keep_nonempty]
    forecast_analysis:     Annotated[str,                  _keep_nonempty]
    final_strategy:        Annotated[str,                  _keep_nonempty]

    # Observability hook — reserved for structured per-agent log entries.
    # operator.add merges concurrent parallel writes without conflicts.
    # Currently unused; replace with LangSmith/OpenTelemetry tracing in production.
    agent_messages:    Annotated[list[dict[str, Any]],    operator.add]
