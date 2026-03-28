import os
import sys
from langgraph.graph import StateGraph, START, END
from langgraph.pregel.remote import RemoteGraph
from langgraph.types import RetryPolicy
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.state import AgentState
from src.orchestrator import orchestrator_node

# ── Agent server URLs ─────────────────────────────────────────────────────────
# Each agent runs as an independent langgraph dev server (see agents/ directory).
# Start all servers with: .\start_agents.ps1
# Override with env vars for production deployments.
_BI_URL          = os.getenv("BI_AGENT_URL",         "http://127.0.0.1:8001")
_MEDIA_URL       = os.getenv("MEDIA_AGENT_URL",       "http://127.0.0.1:8002")
_PRICING_URL     = os.getenv("PRICING_AGENT_URL",     "http://127.0.0.1:8003")
_COORDINATOR_URL = os.getenv("COORDINATOR_AGENT_URL", "http://127.0.0.1:8004")

_retry = RetryPolicy(max_attempts=3)


def create_hospitality_graph():
    """
    Supervisor / Orchestrator-Worker graph.

    Each worker node is a RemoteGraph pointing to an independently running
    langgraph dev server. The orchestrator (in-process) routes via Command,
    fans out to the selected remote agents in parallel, then fans in to the
    remote coordinator for synthesis.

    Flow:
        START
          └─► orchestrator  (in-process, LLM routing via Command)
                ├─► bi_analyzer          RemoteGraph -> :8001
                ├─► media_analyzer       RemoteGraph -> :8002
                └─► pricing_optimizer    RemoteGraph -> :8003
                          └─► strategy_coordinator  RemoteGraph -> :8004
                                    └─► END

    State travels as JSON over HTTP between every node pair.
    Each agent scales, deploys, and restarts independently.
    langgraph-api >= 0.4.21 auto-exposes /a2a/{id} on every server for
    cross-framework (A2A) interoperability at no extra cost.
    """
    builder = StateGraph(AgentState)

    builder.add_node("orchestrator", orchestrator_node)
    builder.add_node("bi_analyzer",
                     RemoteGraph("bi_analyzer",         url=_BI_URL),
                     retry=_retry)
    builder.add_node("media_analyzer",
                     RemoteGraph("media_analyzer",      url=_MEDIA_URL),
                     retry=_retry)
    builder.add_node("pricing_optimizer",
                     RemoteGraph("pricing_optimizer",   url=_PRICING_URL),
                     retry=_retry)
    builder.add_node("strategy_coordinator",
                     RemoteGraph("strategy_coordinator", url=_COORDINATOR_URL),
                     retry=_retry)

    builder.add_edge(START, "orchestrator")
    builder.add_edge("bi_analyzer",       "strategy_coordinator")
    builder.add_edge("media_analyzer",    "strategy_coordinator")
    builder.add_edge("pricing_optimizer", "strategy_coordinator")
    builder.add_edge("strategy_coordinator", END)

    return builder.compile()
