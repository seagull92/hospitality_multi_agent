# Multi-Agent Hospitality Strategy System

This project demonstrates a production-ready, highly scalable multi-agent architecture built using **LangGraph** and **Google Gemini** (via `langchain-google-genai`).

The scenario focuses on a hospitality business needing to synchronize Business Intelligence (BI) insights (e.g., occupancy rates, RevPAR) with Media & Marketing strategy (e.g., ad spend, ROAS). 

## Architecture Overview

The system utilizes a directed graph architecture where specialized AI agents represent different departments within a hospitality group.

1. **State Management (`src/state.py`)**: 
   Defines `AgentState`, a strictly typed dictionary that holds the context. 
   *Scalability Feature:* Uses `Annotated[List[str], operator.add]` to allow agents to append their execution history without overwriting previous steps. It also includes an `additional_insights` dictionary to seamlessly capture data from any newly added N-agents.

2. **The Agents (`src/agents.py`)**:
   - **BI Agent**: Analyzes internal financial and operational metrics.
   - **Media Agent**: Analyzes external marketing spend and performance.
   - **Pricing Agent (Example Nth Agent)**: Demonstrates how a new specialized agent can be dropped in.
   - **Strategy Coordinator**: The Chief Commercial Officer (CCO) agent that synthesizes all preceding analyses into a unified strategy.

3. **The Graph (`src/graph.py`)**:
   Uses LangGraph's `StateGraph`. The nodes are the agents, and the edges define the execution flow.
   *Current Flow*: BI -> Pricing -> Media -> Coordinator.

## Why this is Production Ready & Scalable

1. **Deterministic Execution Flow**: Unlike standard ReAct agents which can get stuck in loops, LangGraph defines a rigid, predictable execution path. You know exactly what data flows where.
2. **Easy Extensibility (N More Agents)**: To add a new agent, you simply:
   - Create a new function in `agents.py`.
   - Add a new node in `graph.py` (`builder.add_node("new_agent", new_func)`).
   - Wire it into the execution path (`builder.add_edge("prev_node", "new_agent")`).
   - The state object (`AgentState`) already supports catching new arbitrary insights.
3. **State Persistence**: By adding a checkpointer (e.g., PostgreSQL or SQLite via `MemorySaver`) when compiling the graph (`builder.compile(checkpointer=...)`), you gain:
   - Resiliency against crashes.
   - Human-in-the-loop capabilities (e.g., pausing the graph before the Media Agent spends money, waiting for human approval).
   - Long-term memory and observability across sessions.
4. **Google Gemini Native**: Utilizes `gemini-2.5-flash` for high-speed, cost-effective reasoning, though it easily swaps to `gemini-2.5-pro` for complex multireasoning tasks.

## Setup & Execution

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure Environment:
   Rename `.env.example` to `.env` and add your Google AI Studio API Key.

3. Run the demonstration:
   ```bash
   python main.py
   ```
   
*Note: The `main.py` file contains mock hospitality data simulating low Q4 occupancy to demonstrate the agents' reasoning capabilities.*
