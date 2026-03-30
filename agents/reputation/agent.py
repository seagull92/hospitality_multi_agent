"""
Guest Experience & Reputation Agent — deployed on pod :8005

READS : query, review_data
WRITES: reputation_analysis

Pod isolation: this file contains ONLY the reputation_agent implementation.
"""
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

_llm = init_chat_model("groq:llama-3.1-8b-instant", temperature=0.2, max_tokens=400)

_SYSTEM_PROMPT = (
    "You are a Guest Experience & Reputation Manager for a hospitality group. "
    "Analyze the provided review data (platform ratings, NPS score, review volume, "
    "sentiment trends, top complaints and praises) and deliver specific, actionable "
    "recommendations to recover or strengthen guest satisfaction and online reputation."
)


def reputation_agent(state: dict) -> dict:
    review_data = state.get("review_data", {})
    query = state.get("query", "")

    if not review_data:
        return {"reputation_analysis": "No review data provided — analysis skipped."}

    response = _llm.invoke([
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"Goal: {query}\n\nReview & Reputation Data:\n{review_data}"),
    ])
    return {"reputation_analysis": response.content}
