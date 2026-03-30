"""
Strategy Coordinator Agent — deployed on pod :8004

READS : query + all available analysis fields written by specialist agents
WRITES: final_strategy

Pod isolation: this file contains ONLY the strategy_coordinator_agent implementation.
This is the synthesis node — it is always the last to run and reads whatever analyses
the activated specialist agents wrote into shared state.
Uses the 70B model because synthesising multiple domain reports requires reasoning quality.
"""
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

_llm = init_chat_model("groq:llama-3.3-70b-versatile", temperature=0.2, max_tokens=500)

_SYSTEM_PROMPT = (
    "You are the Chief Commercial Officer (CCO) of a hospitality group. "
    "Review the independent analyses from your specialist team and synthesize them into a "
    "single, cohesive, immediately actionable business strategy. "
    "Connect insights across disciplines — if pricing is under pressure AND reviews are "
    "falling, explain the link. If ROAS is strong but RevPAR is low, diagnose the gap. "
    "Only use what is provided; never invent data."
)

_ANALYSES_MAP = {
    "Business Intelligence Analysis": "bi_analysis",
    "Media & Marketing Analysis":     "media_analysis",
    "Pricing & Revenue Analysis":     "pricing_analysis",
    "Guest Reputation Analysis":      "reputation_analysis",
    "Revenue Forecast":               "forecast_analysis",
}


def strategy_coordinator_agent(state: dict) -> dict:
    query = state.get("query", "")

    active = {
        label: state.get(field, "")
        for label, field in _ANALYSES_MAP.items()
        if state.get(field, "").strip()
    }

    if not active:
        return {"final_strategy": "No specialist analyses were available to synthesise."}

    analyses_str = "".join(
        f"\n\n--- {label} ---\n{content}" for label, content in active.items()
    )
    user_prompt = (
        f"Original Goal: {query}\n\n"
        f"Specialist Team Reports ({len(active)} source(s)):{analyses_str}"
    )
    response = _llm.invoke([
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=user_prompt),
    ])
    return {"final_strategy": response.content}
