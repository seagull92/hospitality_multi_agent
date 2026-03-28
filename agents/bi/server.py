import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.state import AgentState
from src.agents import bi_agent


def create_graph():
    builder = StateGraph(AgentState)
    builder.add_node("bi_analyzer", bi_agent)
    builder.add_edge(START, "bi_analyzer")
    builder.add_edge("bi_analyzer", END)
    return builder.compile(checkpointer=MemorySaver())
