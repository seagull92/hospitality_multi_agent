from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.state import AgentState
from agents.reputation.agent import reputation_agent


def create_graph():
    builder = StateGraph(AgentState)
    builder.add_node("reputation_agent", reputation_agent)
    builder.add_edge(START, "reputation_agent")
    builder.add_edge("reputation_agent", END)
    return builder.compile(checkpointer=MemorySaver())
