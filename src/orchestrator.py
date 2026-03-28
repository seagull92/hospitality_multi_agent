from typing import List, Literal
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Command
from dotenv import load_dotenv

load_dotenv()

# temperature=0 for deterministic, reproducible routing decisions
_router_llm = init_chat_model(
    "groq:llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=512,
)


class RoutingDecision(BaseModel):
    """Structured output schema for the orchestrator's routing decision."""
    agents: List[Literal["bi_analyzer", "media_analyzer", "pricing_optimizer"]] = Field(
        description=(
            "List of worker agents to activate. "
            "Select only those relevant to the query and available data."
        )
    )
    reasoning: str = Field(
        description="One-sentence explanation of why these agents were selected."
    )


_router = _router_llm.with_structured_output(RoutingDecision)

_SYSTEM_PROMPT = """You are the Orchestrator of a hospitality intelligence platform.
Your sole job is to analyze the incoming query and available data, then decide which
specialist worker agents must be activated.

Available workers:
- bi_analyzer       - use when query involves occupancy, RevPAR, booking pace, or financial performance
- media_analyzer    - use when query involves ad spend, ROAS, CTR, CPA, or marketing channel performance
- pricing_optimizer - use when query involves pricing strategy, rate adjustments, or revenue management

Rules:
1. Activate ONLY agents whose domain is relevant to the query.
2. You may activate all three for comprehensive analysis requests.
3. Never activate an agent if its data domain is not present in the available data keys."""


def orchestrator_node(
    state: dict,
) -> Command[Literal["bi_analyzer", "media_analyzer", "pricing_optimizer"]]:
    """
    LLM-powered Orchestrator using the Command pattern (LangGraph 1.x standard).

    Returns a Command that atomically updates state AND fans out to the
    selected worker nodes in parallel — replacing the older pattern of
    returning a dict + a separate add_conditional_edges() call.

    Upgrade path:
    - Swap each worker node for RemoteGraph(url=...) for microservice scaling.
    - Deploy via langgraph-api >= 0.4.21 to auto-expose /a2a/{id} endpoints
      for cross-framework interoperability (LangGraph <-> CrewAI <-> custom).
    """
    query = state.get("query", "")
    bi_data = state.get("bi_data", {})
    media_data = state.get("media_data", {})

    user_prompt = (
        f"Query: {query}\n\n"
        f"Available BI data fields   : {list(bi_data.keys())}\n"
        f"Available Media data fields: {list(media_data.keys())}"
    )

    decision: RoutingDecision = _router.invoke([
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ])

    return Command(
        update={
            "next_agents": decision.agents,
            "routing_reasoning": decision.reasoning,
            "history": [f"Orchestrator activated: {', '.join(decision.agents)}"],
        },
        goto=decision.agents,
    )
