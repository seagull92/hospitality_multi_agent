# PROD — see agents/bi/server.py for full deployment notes.
# Summary of what changes in a real pod deployment:
#   - Run via langgraph-api Docker image, not `langgraph dev`
#   - MemorySaver is fine for this stateless single-step agent
#   - Package installed via pip install -e . inside the container
#   - Set GROQ_API_KEY and LANGCHAIN_API_KEY as pod environment variables
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.state import AgentState
from agents.coordinator.agent import strategy_coordinator_agent


def create_graph():
    builder = StateGraph(AgentState)
    builder.add_node("strategy_coordinator", strategy_coordinator_agent)
    builder.add_edge(START, "strategy_coordinator")
    builder.add_edge("strategy_coordinator", END)
    return builder.compile(checkpointer=MemorySaver())
