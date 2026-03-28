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
    agents: List[Literal[
        "bi_analyzer",
        "media_analyzer",
        "pricing_optimizer",
        "reputation_agent",
        "revenue_forecast_agent",
    ]] = Field(
        description=(
            "List of worker agents to activate. "
            "Select ONLY those whose domain is relevant to the query AND whose "
            "required data fields are non-empty in the available data."
        )
    )
    reasoning: str = Field(
        description="One-sentence explanation of which agents were selected and why."
    )


_router = _router_llm.with_structured_output(RoutingDecision)

_SYSTEM_PROMPT = """You are the Orchestrator of a hospitality intelligence platform.
Your sole job is to analyze the incoming query and the available data fields, then decide
which specialist worker agents must be activated.

Available workers and their required data:
- bi_analyzer            requires: BI data fields (occupancy, RevPAR, booking pace, financial metrics)
- media_analyzer         requires: Media data fields (ad spend, ROAS, CTR, CPA, campaign data)
- pricing_optimizer      requires: BI data fields (competitor pricing, ADR, occupancy) — pricing context
- reputation_agent       requires: Review data fields (ratings, NPS, sentiment, review volume)
- revenue_forecast_agent requires: Forecast data fields (trends, market growth, demand projections)

Strict rules:
1. NEVER activate an agent whose required data fields are EMPTY — it has nothing to analyze.
2. Activate ONLY agents whose domain directly addresses the query.
3. You may activate multiple agents when the query spans several domains AND data is present.
4. For comprehensive queries with all data present, activate all relevant agents."""


def orchestrator_node(
    state: dict,
) -> Command[Literal["bi_analyzer", "media_analyzer", "pricing_optimizer", "reputation_agent", "revenue_forecast_agent"]]:
    """
    LLM-powered Orchestrator using the Command pattern (LangGraph 1.x standard).

    Returns a Command that atomically updates state AND fans out to the
    selected worker nodes in parallel. Each worker is a RemoteGraph pointing
    to an independently running langgraph dev server (see agents/ directory).
    """
    query = state.get("query", "")
    bi_data = state.get("bi_data", {})
    media_data = state.get("media_data", {})

    review_data   = state.get("review_data",   {})
    forecast_data = state.get("forecast_data", {})

    user_prompt = (
        f"Query: {query}\n\n"
        f"Available BI data fields      : {list(bi_data.keys()) or 'EMPTY'}\n"
        f"Available Media data fields   : {list(media_data.keys()) or 'EMPTY'}\n"
        f"Available Review data fields  : {list(review_data.keys()) or 'EMPTY'}\n"
        f"Available Forecast data fields: {list(forecast_data.keys()) or 'EMPTY'}"
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
