from langgraph.graph import StateGraph, START, END
from typing import TypedDict
import sys
import os

# Add src to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state import AgentState
from src.agents import bi_agent, media_agent, pricing_agent, strategy_coordinator_agent

def create_hospitality_graph():
    """
    Builds and compiles the LangGraph workflow for the BI & Media Hospitality scenario.
    
    Architecture & Scalability Notes:
    - This graph is defined sequentially for clear data flow: BI -> Media -> Pricing -> Coordinator.
    - To scale to N agents, you simply `builder.add_node("new_agent", new_agent_func)` 
      and insert it into the edge flow where its dependencies are met.
    - LangGraph supports Checkpointers (e.g., PostgreSQL, SQLite) for production state persistence,
      human-in-the-loop approvals, and parallel execution.
    """
    
    # 1. Initialize the State Graph with our typed state
    builder = StateGraph(AgentState)
    
    # 2. Add nodes for each agent
    builder.add_node("bi_analyzer", bi_agent)
    builder.add_node("media_analyzer", media_agent)
    
    # Example of an Nth agent added for scalability
    builder.add_node("pricing_optimizer", pricing_agent)
    
    # The final synthesizer
    builder.add_node("strategy_coordinator", strategy_coordinator_agent)
    
    # 3. Define the flow (Edges)
    # We use a sequential flow here. In a highly parallel production environment,
    # you could fan-out from START to BI and Media, then fan-in to Strategy.
    
    builder.add_edge(START, "bi_analyzer")
    
    # BI flows to Pricing (since pricing needs BI occupancy data)
    builder.add_edge("bi_analyzer", "pricing_optimizer")
    
    # Pricing flows to Media (or they could be independent)
    builder.add_edge("pricing_optimizer", "media_analyzer")
    
    # Media flows to the final coordinator
    builder.add_edge("media_analyzer", "strategy_coordinator")
    
    # Coordinator finishes the workflow
    builder.add_edge("strategy_coordinator", END)
    
    # 4. Compile the graph
    # In production, you would pass `checkpointer=MemorySaver()` or a DB checkpointer here
    # to enable memory, resumption, and observability.
    graph = builder.compile()
    
    return graph
