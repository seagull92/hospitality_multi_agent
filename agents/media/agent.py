"""
Media & Marketing Agent — deployed on pod :8002

READS : query, media_data
WRITES: media_analysis

Pod isolation: this file contains ONLY the media_agent implementation.
"""
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

_llm = init_chat_model("groq:llama-3.1-8b-instant", temperature=0.2, max_tokens=400)

_SYSTEM_PROMPT = (
    "You are an expert Media & Performance Marketing Director for a hospitality group. "
    "Analyze the provided media data (ad spend, ROAS by channel, CTR, CPA, campaign data) "
    "and determine how marketing dollars are currently performing and where they should "
    "be reallocated to maximise bookings and revenue."
)


def media_agent(state: dict) -> dict:
    media_data = state.get("media_data", {})
    query = state.get("query", "")

    if not media_data:
        return {"media_analysis": "No media data provided — analysis skipped."}

    response = _llm.invoke([
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"Goal: {query}\n\nMedia Data:\n{media_data}"),
    ])
    return {"media_analysis": response.content}
