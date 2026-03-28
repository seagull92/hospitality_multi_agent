import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.state import AgentState
from src.agents import strategy_coordinator_agent


def create_graph():
    builder = StateGraph(AgentState)
    builder.add_node("strategy_coordinator", strategy_coordinator_agent)
    builder.add_edge(START, "strategy_coordinator")
    builder.add_edge("strategy_coordinator", END)
    return builder.compile(checkpointer=MemorySaver())
