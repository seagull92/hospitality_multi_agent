from typing import TypedDict, Annotated, List, Dict, Any
import operator

class AgentState(TypedDict):
    """
    The shared state for the multi-agent system.
    This structure is designed to be easily extensible. When adding N more agents,
    they can either read from existing state keys or you can add new keys here.
    """
    
    # Input from the user/trigger
    query: str
    
    # Data context provided to the system
    bi_data: Dict[str, Any]
    media_data: Dict[str, Any]
    
    # Outputs from specific agents
    # We use Annotated[List[str], operator.add] to allow agents to append findings
    bi_analysis: str
    media_analysis: str
    
    # Final consolidated strategy
    final_strategy: str
    
    # A list to keep track of the steps executed for observability
    history: Annotated[List[str], operator.add]
    
    # A dictionary to hold outputs from any newly added agent (Scalability feature)
    # E.g., additional_insights["pricing_agent"] = "..."
    additional_insights: Dict[str, str]
