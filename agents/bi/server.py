# PROD — How to run this pod in production:
#   Option A (recommended): use the official langgraph-api Docker image.
#     The image reads langgraph.json, installs dependencies, and exposes the
#     LangGraph HTTP API on port 8000.  Run one container per agent.
#     docker run -p 8001:8000 \
#       -e GROQ_API_KEY=$GROQ_API_KEY \
#       -v $(pwd):/deps/app \
#       langchain/langgraph-api:latest
#
#   Option B: `langgraph dev` (current — development only, not for production).
#     It uses a hot-reloading dev server and is NOT hardened for traffic.
#
# PROD — Checkpointer:
#   MemorySaver is in-process only. For a stateless single-step agent
#   (START -> node -> END) it is safe — each HTTP invocation gets a new thread.
#   If you ever add multi-step logic or need replay, replace with:
#     from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
#     checkpointer = AsyncPostgresSaver.from_conn_string(os.getenv("DATABASE_URL"))
#
# PROD — State schema (AgentState):
#   Imported from src.state via pip install -e . (pyproject.toml).
#   In a real pod: bake the package into the Docker image at build time.
#   The state is serialised as JSON over HTTP by RemoteGraph — no shared memory.
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
