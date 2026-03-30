"""
Business Intelligence Agent — deployed on pod :8001

READS : query, bi_data
WRITES: bi_analysis

Pod isolation: this file contains ONLY the bi_agent implementation.
Each pod imports only its own agent module, not the full src/agents.py.
"""
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

_llm = init_chat_model("groq:llama-3.1-8b-instant", temperature=0.2, max_tokens=400)

_SYSTEM_PROMPT = (
    "You are an expert Business Intelligence Analyst for a hospitality group. "
    "Analyze the provided BI data (occupancy rates, RevPAR, booking pace, cancellations, "
    "competitor pricing) and extract specific, actionable insights. Focus on revenue "
    "opportunities, underperforming periods, and financial health of the properties."
)


def bi_agent(state: dict) -> dict:
    bi_data = state.get("bi_data", {})
    query = state.get("query", "")

    if not bi_data:
        return {"bi_analysis": "No BI data provided — analysis skipped."}

    response = _llm.invoke([
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"Goal: {query}\n\nBI Data:\n{bi_data}"),
    ])
    return {"bi_analysis": response.content}
