# PROD — see agents/bi/server.py for full deployment notes.
# Summary of what changes in a real pod deployment:
#   - Run via langgraph-api Docker image, not `langgraph dev`
#   - MemorySaver is fine for this stateless single-step agent
#   - Package installed via pip install -e . inside the container
#   - Set GROQ_API_KEY and LANGCHAIN_API_KEY as pod environment variables
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.state import AgentState
from agents.media.agent import media_agent


def create_graph():
    builder = StateGraph(AgentState)
    builder.add_node("media_analyzer", media_agent)
    builder.add_edge(START, "media_analyzer")
    builder.add_edge("media_analyzer", END)
    return builder.compile(checkpointer=MemorySaver())
