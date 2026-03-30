from typing import Literal

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Command
from pydantic import BaseModel, Field

load_dotenv()

# temperature=0 for deterministic, reproducible routing decisions
_router_llm = init_chat_model(
    "groq:llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=256,
)


class RoutingDecision(BaseModel):
    """Structured output schema for the orchestrator's routing decision."""
    agents: list[Literal[
        "bi_analyzer",
        "media_analyzer",
        "pricing_optimizer",
        "reputation_agent",
        "revenue_forecast_agent",
    ]] = Field(description="Names of the specialist agents to activate.")
    reasoning: str = Field(
        description="One sentence explaining which agents were selected and why."
    )


_router = _router_llm.with_structured_output(RoutingDecision)

_SYSTEM_PROMPT = """\
You are a routing agent for a hospitality revenue intelligence system.

Task: given a natural-language query and a data manifest, return the minimal
set of specialist agents to activate.

Agent registry:
  bi_analyzer            data: bi_data
                         capability: financial KPI analysis
                         fields: occupancy_rate, revpar, adr, booking_pace
  media_analyzer         data: media_data
                         capability: paid media performance
                         fields: monthly_budget, google_ads_roas, meta_ads_roas, ctr
  pricing_optimizer      data: bi_data
                         capability: rate strategy and competitive positioning
                         fields: competitor_pricing, revpar, occupancy_rate, adr
  reputation_agent       data: review_data
                         capability: guest satisfaction and online reputation
                         fields: tripadvisor_rating, google_rating, nps_score
  revenue_forecast_agent data: forecast_data
                         capability: 12-month revenue projection and demand modelling
                         fields: revenue_trend_ytd, market_growth_rate

Routing logic:
  - Exclude any agent whose required data domain is absent from the manifest.
  - Select agents whose capability is materially relevant to the query.
  - When a query spans multiple domains and all data is present, activate all
    relevant agents.

Return a RoutingDecision with selected agent names and a one-sentence justification.\
"""


def orchestrator_node(
    state: dict,
) -> Command[
    Literal[
        "bi_analyzer",
        "media_analyzer",
        "pricing_optimizer",
        "reputation_agent",
        "revenue_forecast_agent",
    ]
]:
    """
    LLM-powered Orchestrator using the Command pattern (LangGraph 1.x standard).

    Returns a Command that atomically updates state AND fans out to the
    selected worker nodes in parallel. Each worker is a RemoteGraph pointing
    to an independently running langgraph dev server (see agents/ directory).
    """
    query = state.get("query", "")
    bi_data = state.get("bi_data", {})
    media_data = state.get("media_data", {})

    review_data = state.get("review_data", {})
    forecast_data = state.get("forecast_data", {})

    user_prompt = (
        f"Query: {query}\n\n"
        f"Data manifest:\n"
        f"  bi_data:       {list(bi_data.keys()) if bi_data else 'not provided'}\n"
        f"  media_data:    {list(media_data.keys()) if media_data else 'not provided'}\n"
        f"  review_data:   {list(review_data.keys()) if review_data else 'not provided'}\n"
        f"  forecast_data: {list(forecast_data.keys()) if forecast_data else 'not provided'}"
    )

    decision: RoutingDecision = _router.invoke([
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ])

    return Command(
        update={
            "next_agents": decision.agents,
            "routing_reasoning": decision.reasoning,
        },
        goto=decision.agents,
    )
