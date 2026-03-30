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

# Agent registry: maps each agent to its required data domain and capability.
# Data-availability filtering is done deterministically before any LLM call.
# The LLM only receives agents whose data domain is actually populated.
_AGENT_REGISTRY: dict[str, dict[str, str]] = {
    "bi_analyzer": {
        "domain":     "bi_data",
        "capability": "financial KPI analysis (occupancy, RevPAR, ADR, booking pace)",
    },
    "pricing_optimizer": {
        "domain":     "bi_data",
        "capability": "rate strategy and competitive positioning",
    },
    "media_analyzer": {
        "domain":     "media_data",
        "capability": "paid media performance (ad spend, ROAS, CTR by channel)",
    },
    "reputation_agent": {
        "domain":     "review_data",
        "capability": "guest satisfaction and online reputation management",
    },
    "revenue_forecast_agent": {
        "domain":     "forecast_data",
        "capability": "12-month revenue projection and demand modelling",
    },
}

_SYSTEM_PROMPT = """\
You are a routing agent for a hospitality revenue intelligence system.

Select the specialist agents best suited to answer the query.
Choose only from the available specialists listed below.

Available specialists:
{available_agents}

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
    Two-stage routing using the LangGraph 1.x Command pattern.

    Stage 1 — deterministic pre-filter (no LLM):
      Exclude any agent whose data domain is absent from state.
      This is a Python dict lookup — fast, free, and testable.

    Stage 2 — LLM selection:
      The model receives only the pre-filtered agent list and the raw
      user query. It selects agents based purely on query intent vs.
      agent capability. No internal state details are exposed to the LLM.

    In LangSmith the human message is the raw user query — nothing else.
    """
    query = state.get("query", "")
    data_domains = {
        "bi_data":       state.get("bi_data",       {}),
        "media_data":    state.get("media_data",     {}),
        "review_data":   state.get("review_data",    {}),
        "forecast_data": state.get("forecast_data",  {}),
    }

    # Stage 1: exclude agents whose data domain is absent — O(n) lookup
    available = {
        name: meta
        for name, meta in _AGENT_REGISTRY.items()
        if data_domains.get(meta["domain"])
    }

    # Stage 2: LLM picks from available agents based on query intent only
    agents_block = "\n".join(
        f"  {name}: {meta['capability']}" for name, meta in available.items()
    )
    system_prompt = _SYSTEM_PROMPT.format(available_agents=agents_block)

    decision: RoutingDecision = _router.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=query),
    ])

    return Command(
        update={
            "next_agents": decision.agents,
            "routing_reasoning": decision.reasoning,
        },
        goto=decision.agents,
    )
