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
