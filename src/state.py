from typing import Annotated, List, Dict, Any
from typing_extensions import TypedDict
import operator


def _keep_last(current: Any, update: Any) -> Any:
    """Last writer wins — safe for input fields (query, bi_data, etc.) that are
    never mutated by agents and will always carry the same value across parallel writes."""
    return update


def _keep_nonempty(current: Any, update: Any) -> Any:
    """Keep the most recent non-empty value. Used for agent output fields (bi_analysis,
    media_analysis, final_strategy): parallel agents that don't own that field return
    an empty string, which should never overwrite real content written by the owning agent."""
    return update if update else current


def _merge_dicts(current: Dict, update: Dict) -> Dict:
    """Merge two dicts; used for additional_insights so each agent can add its key
    without overwriting what a parallel agent already wrote."""
    return {**current, **update}


class AgentState(TypedDict):
    # Input from the user/trigger
    query:             Annotated[str,                      _keep_last]

    # Data context provided to the system
    bi_data:           Annotated[Dict[str, Any],           _keep_last]
    media_data:        Annotated[Dict[str, Any],           _keep_last]

    # Orchestrator routing
    next_agents:       Annotated[List[str],                _keep_last]
    routing_reasoning: Annotated[str,                      _keep_last]

    # Agent outputs — use _keep_nonempty so a parallel agent returning "" never
    # overwrites content written by the agent that owns that field
    bi_analysis:       Annotated[str,                      _keep_nonempty]
    media_analysis:    Annotated[str,                      _keep_nonempty]
    final_strategy:    Annotated[str,                      _keep_nonempty]

    # Append-only logs (operator.add = concatenate lists across parallel writes)
    history:           Annotated[List[str],                operator.add]
    agent_messages:    Annotated[List[Dict[str, Any]],     operator.add]

    # Extensible insights dict — merged so parallel agents don't overwrite each other
    additional_insights: Annotated[Dict[str, str],         _merge_dicts]
