from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.state import AgentState
from agents.forecast.agent import revenue_forecast_agent


def create_graph():
    builder = StateGraph(AgentState)
    builder.add_node("revenue_forecast_agent", revenue_forecast_agent)
    builder.add_edge(START, "revenue_forecast_agent")
    builder.add_edge("revenue_forecast_agent", END)
    return builder.compile(checkpointer=MemorySaver())
