"""
Agent function registry.

Each agent's implementation lives in its own pod-isolated module under agents/.
This file re-exports them for monorepo convenience — the main graph and tests
can import from here without knowing the pod layout.

In a true multi-pod deployment each pod only installs and imports its own module:
  pod :8001  →  agents.bi.agent.bi_agent
  pod :8002  →  agents.media.agent.media_agent
  pod :8003  →  agents.pricing.agent.pricing_agent
  pod :8004  →  agents.coordinator.agent.strategy_coordinator_agent
  pod :8005  →  agents.reputation.agent.reputation_agent
  pod :8006  →  agents.forecast.agent.revenue_forecast_agent
"""
from agents.bi.agent import bi_agent
from agents.media.agent import media_agent
from agents.pricing.agent import pricing_agent
from agents.coordinator.agent import strategy_coordinator_agent
from agents.reputation.agent import reputation_agent
from agents.forecast.agent import revenue_forecast_agent

__all__ = [
    "bi_agent",
    "media_agent",
    "pricing_agent",
    "strategy_coordinator_agent",
    "reputation_agent",
    "revenue_forecast_agent",
]
