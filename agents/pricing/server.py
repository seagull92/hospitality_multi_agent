from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.state import AgentState
from agents.pricing.agent import pricing_agent


def create_graph():
    builder = StateGraph(AgentState)
    builder.add_node("pricing_optimizer", pricing_agent)
    builder.add_edge(START, "pricing_optimizer")
    builder.add_edge("pricing_optimizer", END)
    return builder.compile(checkpointer=MemorySaver())
