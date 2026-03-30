from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.state import AgentState
from agents.bi.agent import bi_agent


def create_graph():
    builder = StateGraph(AgentState)
    builder.add_node("bi_analyzer", bi_agent)
    builder.add_edge(START, "bi_analyzer")
    builder.add_edge("bi_analyzer", END)
    return builder.compile(checkpointer=MemorySaver())
