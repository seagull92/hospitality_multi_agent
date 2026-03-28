from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

llm = init_chat_model(
    "groq:llama-3.3-70b-versatile",
    temperature=0.2,
    max_tokens=2048,
)

def _log_read(agent: str, keys: dict) -> dict:
    """Build an agent_messages entry documenting what this agent READ from state."""
    return {
        "agent": agent,
        "action": "READ",
        "state_keys": list(keys.keys()),
        "preview": {k: str(v)[:120] + "..." if len(str(v)) > 120 else str(v)
                    for k, v in keys.items()},
    }


def _log_write(agent: str, keys: dict) -> dict:
    """Build an agent_messages entry documenting what this agent WROTE to state."""
    return {
        "agent": agent,
        "action": "WRITE",
        "state_keys": list(keys.keys()),
        "preview": {k: str(v)[:120] + "..." if len(str(v)) > 120 else str(v)
                    for k, v in keys.items()},
    }


def bi_agent(state):
    """
    Business Intelligence Agent.
    READS : query, bi_data
    WRITES: bi_analysis  (consumed by strategy_coordinator)
    """
    bi_data = state.get("bi_data", {})
    query   = state.get("query", "")


    system_prompt = (
        "You are an expert Business Intelligence Analyst for a hospitality group. "
        "Your task is to analyze the provided BI data (occupancy rates, RevPAR, booking pace, cancellations) "
        "and extract actionable insights. Focus on revenue opportunities, identifying low-performing periods, "
        "and summarizing the financial health of the properties."
    )
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Target Query: {query}\n\nBI Data:\n{bi_data}"),
    ])


    return {
        "bi_analysis": response.content,
        "history": ["bi_analyzer wrote bi_analysis to state"],
        "agent_messages": [
            _log_read("bi_analyzer",  {"query": query, "bi_data": bi_data}),
            _log_write("bi_analyzer", {"bi_analysis": response.content}),
        ],
    }


def media_agent(state):
    """
    Media & Marketing Agent.
    READS : query, media_data
    WRITES: media_analysis  (consumed by strategy_coordinator)
    """
    media_data = state.get("media_data", {})
    query      = state.get("query", "")


    system_prompt = (
        "You are an expert Media & Performance Marketing Director for a hospitality group. "
        "Your task is to analyze the provided Media data (Ad spend, ROAS by channel, CTR, CPA) "
        "and determine how marketing dollars are currently performing and where they should be reallocated."
    )
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Target Query: {query}\n\nMedia Data:\n{media_data}"),
    ])


    return {
        "media_analysis": response.content,
        "history": ["media_analyzer wrote media_analysis to state"],
        "agent_messages": [
            _log_read("media_analyzer",  {"query": query, "media_data": media_data}),
            _log_write("media_analyzer", {"media_analysis": response.content}),
        ],
    }


def strategy_coordinator_agent(state):
    """
    Strategy Coordinator — the merge/synthesis node.
    READS : query + all available agent analysis fields
    WRITES: final_strategy

    Dynamically synthesizes whatever analyses are present in state.
    This handles any subset of agents being activated — 1, 2, 3, or all 5.
    All communication happened via shared state — no direct agent-to-agent calls.
    """
    query = state.get("query", "")

    analyses_map = {
        "Business Intelligence Analysis": state.get("bi_analysis",         ""),
        "Media & Marketing Analysis":     state.get("media_analysis",      ""),
        "Pricing & Revenue Analysis":     state.get("pricing_analysis",    ""),
        "Guest Reputation Analysis":      state.get("reputation_analysis", ""),
        "Revenue Forecast":               state.get("forecast_analysis",   ""),
    }
    for agent_name, insight in state.get("additional_insights", {}).items():
        analyses_map[agent_name.replace("_", " ").title()] = insight

    active = {k: v for k, v in analyses_map.items() if v.strip()}

    analyses_str = "".join(
        f"\n\n--- {source} ---\n{content}" for source, content in active.items()
    )

    system_prompt = (
        "You are the Chief Commercial Officer (CCO) of a hospitality group. "
        "Review the independent analyses provided by your specialist team and "
        "synthesize them into a single, cohesive, and immediately actionable business strategy. "
        "Connect insights across disciplines — if pricing is under pressure AND reviews are falling, "
        "explain the link. If ROAS is strong but RevPAR is low, diagnose the gap. "
        "Only use what is provided; do not invent data."
    )
    user_prompt = (
        f"Original Goal: {query}\n\n"
        f"Specialist Team Reports ({len(active)} source(s)):"
        f"{analyses_str}"
    )
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])

    return {
        "final_strategy": response.content,
        "history": [f"strategy_coordinator synthesized {len(active)} analyses -> final_strategy"],
        "agent_messages": [
            _log_read("strategy_coordinator",  {"sources_read": list(active.keys())}),
            _log_write("strategy_coordinator", {"final_strategy": response.content}),
        ],
    }


def pricing_agent(state):
    """
    Revenue Management & Pricing Agent.
    READS : query, bi_data  (raw — runs in parallel with bi_analyzer)
    WRITES: additional_insights["pricing_agent"]  (consumed by strategy_coordinator)
    """
    bi_data = state.get("bi_data", {})
    query   = state.get("query", "")


    system_prompt = (
        "You are a Revenue Management & Pricing Specialist for a hospitality group. "
        "Based on the raw BI data provided, recommend specific percentage price adjustments "
        "for upcoming periods, with clear justification for each recommendation."
    )
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Goal: {query}\n\nRaw BI Data:\n{bi_data}"),
    ])

    return {
        "pricing_analysis": response.content,
        "history": ["pricing_optimizer wrote pricing_analysis to state"],
        "agent_messages": [
            _log_read("pricing_optimizer",  {"query": query, "bi_data": bi_data}),
            _log_write("pricing_optimizer", {"pricing_analysis": response.content}),
        ],
    }


def reputation_agent(state):
    """
    Guest Experience & Reputation Agent.
    READS : query, review_data
    WRITES: reputation_analysis  (consumed by strategy_coordinator)
    """
    review_data = state.get("review_data", {})
    query       = state.get("query", "")

    system_prompt = (
        "You are a Guest Experience & Reputation Manager for a hospitality group. "
        "Analyze the provided review data (platform ratings, NPS score, review volume, "
        "sentiment trends, top complaints and praises) and deliver specific, actionable "
        "recommendations to recover or strengthen guest satisfaction and online reputation."
    )
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Goal: {query}\n\nReview & Reputation Data:\n{review_data}"),
    ])

    return {
        "reputation_analysis": response.content,
        "history": ["reputation_agent wrote reputation_analysis to state"],
        "agent_messages": [
            _log_read("reputation_agent",  {"query": query, "review_data": review_data}),
            _log_write("reputation_agent", {"reputation_analysis": response.content}),
        ],
    }


def revenue_forecast_agent(state):
    """
    Revenue Forecasting Agent.
    READS : query, bi_data, forecast_data
    WRITES: forecast_analysis  (consumed by strategy_coordinator)
    """
    bi_data       = state.get("bi_data",       {})
    forecast_data = state.get("forecast_data", {})
    query         = state.get("query", "")

    system_prompt = (
        "You are a Revenue Forecasting Analyst for a hospitality group. "
        "Using the provided historical BI performance data and forward-looking market indicators, "
        "build a detailed revenue forecast with specific numerical projections, "
        "seasonality insights, and strategic recommendations for the next 12 months."
    )
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Goal: {query}\n\nBI Performance Data:\n{bi_data}\n\nForecast Indicators:\n{forecast_data}"),
    ])

    return {
        "forecast_analysis": response.content,
        "history": ["revenue_forecast_agent wrote forecast_analysis to state"],
        "agent_messages": [
            _log_read("revenue_forecast_agent",  {"query": query, "bi_data": bi_data, "forecast_data": forecast_data}),
            _log_write("revenue_forecast_agent", {"forecast_analysis": response.content}),
        ],
    }
