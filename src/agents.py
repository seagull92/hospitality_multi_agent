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
    READS : query, bi_analysis, media_analysis, additional_insights
    WRITES: final_strategy

    This is where BI and Media data CONVERGE: the coordinator reads outputs
    written by bi_analyzer and media_analyzer and synthesizes them.
    All communication happened via shared state — no direct agent-to-agent calls.
    """
    bi_analysis        = state.get("bi_analysis", "")
    media_analysis     = state.get("media_analysis", "")
    additional_insights = state.get("additional_insights", {})
    query              = state.get("query", "")


    extra_insights_str = ""
    for agent_name, insight in additional_insights.items():
        extra_insights_str += f"\n\n{agent_name.capitalize()} Insights:\n{insight}"

    system_prompt = (
        "You are the Chief Commercial Officer (CCO) of a hospitality group. "
        "Your task is to review the independent analyses from your Business Intelligence team "
        "and your Media/Marketing team, and synthesize them into a cohesive, actionable business strategy. "
        "If BI identifies a low-occupancy period, how should Media adjust? If Media has high ROAS but BI shows low RevPAR, why?"
    )
    user_prompt = (
        f"Original Goal: {query}\n\n"
        f"BI Analysis (from bi_analyzer via shared state):\n{bi_analysis}\n\n"
        f"Media Analysis (from media_analyzer via shared state):\n{media_analysis}"
        f"{extra_insights_str}"
    )
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ])


    return {
        "final_strategy": response.content,
        "history": ["strategy_coordinator merged bi_analysis + media_analysis -> final_strategy"],
        "agent_messages": [
            _log_read("strategy_coordinator", {
                "bi_analysis": bi_analysis,
                "media_analysis": media_analysis,
                "additional_insights_keys": list(additional_insights.keys()),
            }),
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

    current_insights = state.get("additional_insights", {})
    current_insights["pricing_agent"] = response.content


    return {
        "additional_insights": current_insights,
        "history": ["pricing_optimizer wrote pricing recommendations to additional_insights"],
        "agent_messages": [
            _log_read("pricing_optimizer",  {"query": query, "bi_data": bi_data}),
            _log_write("pricing_optimizer", {"additional_insights[pricing_agent]": response.content}),
        ],
    }
