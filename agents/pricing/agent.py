"""
Revenue Management & Pricing Agent — deployed on pod :8003

READS : query, bi_data  (occupancy, RevPAR, ADR, competitor pricing are the pricing inputs)
WRITES: pricing_analysis

Pod isolation: this file contains ONLY the pricing_agent implementation.
Note: competitor pricing and ADR live in bi_data — this is intentional since both the
BI analyst and the pricing specialist need the same financial metrics as inputs.
"""
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

_llm = init_chat_model("groq:llama-3.1-8b-instant", temperature=0.2, max_tokens=400)

_SYSTEM_PROMPT = (
    "You are a Revenue Management & Pricing Specialist for a hospitality group. "
    "Based on the BI data provided (occupancy rate, RevPAR, ADR, competitor pricing, "
    "booking pace), recommend specific percentage price adjustments for upcoming periods. "
    "Give a clear rationale and quantified projections for each recommendation."
)


def pricing_agent(state: dict) -> dict:
    bi_data = state.get("bi_data", {})
    query = state.get("query", "")

    if not bi_data:
        return {"pricing_analysis": "No BI/pricing data provided — analysis skipped."}

    response = _llm.invoke([
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"Goal: {query}\n\nBI & Competitive Data:\n{bi_data}"),
    ])
    return {"pricing_analysis": response.content}
