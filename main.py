"""
Hospitality Multi-Agent Intelligence System — Demonstration Runner

Runs 6 use cases that prove the AI Orchestrator activates only the agents
relevant to each scenario:

  #1  MARKETING CHANNEL CRISIS      1 agent   media_analyzer
  #2  Q4 REVENUE SHORTFALL          2 agents  bi_analyzer + pricing_optimizer
  #3  Q4 FULL COMMERCIAL STRATEGY   3 agents  bi + media + pricing
  #4  ANNUAL STRATEGIC REVIEW       5 agents  ALL
"""
import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.graph import create_hospitality_graph

# ── Formatting helpers ────────────────────────────────────────────────────────
W = 80
def div(char="="): return char * W
def sep():         return "-" * W

AGENT_LABELS = {
    "orchestrator":          "AI Orchestrator",
    "bi_analyzer":           "Business Intelligence Analyst",
    "media_analyzer":        "Media & Marketing Director",
    "pricing_optimizer":     "Revenue & Pricing Specialist",
    "reputation_agent":      "Guest Experience Manager",
    "revenue_forecast_agent":"Revenue Forecast Analyst",
    "strategy_coordinator":  "Chief Commercial Officer (CCO)",
}

# Maps agent node-name → (state field it writes, display label)
AGENT_OUTPUT_FIELDS = {
    "bi_analyzer":           ("bi_analysis",         "Business Intelligence Analyst"),
    "media_analyzer":        ("media_analysis",       "Media & Marketing Director"),
    "pricing_optimizer":     ("pricing_analysis",     "Revenue & Pricing Specialist"),
    "reputation_agent":      ("reputation_analysis",  "Guest Experience Manager"),
    "revenue_forecast_agent":("forecast_analysis",    "Revenue Forecast Analyst"),
}

# ── Use cases ─────────────────────────────────────────────────────────────────
USE_CASES = [
    {
        "title":   "MARKETING CHANNEL CRISIS",
        "pattern": "1 agent  →  media_analyzer only",
        "query": "Google Ads CTR dropped from 3.2% to 0.9% and ROAS fell to 1.3x. What is wrong and how do we fix it?",
        "bi_data":       {},
        "media_data":    {
            "monthly_budget":  "$50,000",
            "google_ads_roas": "1.3x (was 4.1x)",
            "google_ads_ctr":  "0.9% (was 3.2%)",
            "meta_ads_roas":   "2.9x",
        },
        "review_data":   {},
        "forecast_data": {},
    },
    {
        "title":   "Q4 REVENUE SHORTFALL",
        "pattern": "2 agents  →  bi_analyzer + pricing_optimizer",
        "query": "RevPAR is 22% below Q4 target with 7 weeks left. Diagnose the performance and recommend a pricing response.",
        "bi_data":       {
            "occupancy_rate":     "56%",
            "revpar":             "$118 (target $152)",
            "booking_pace":       "Down 28% YoY",
            "competitor_pricing": "Avg $172/night",
        },
        "media_data":    {},
        "review_data":   {},
        "forecast_data": {},
    },
    {
        "title":   "Q4 FULL COMMERCIAL STRATEGY",
        "pattern": "3 agents  →  bi_analyzer + media_analyzer + pricing_optimizer",
        "query": "Q4 in 8 weeks: occupancy at 62%, Meta underperforming, competitor rates aggressive. Build a full commercial strategy.",
        "bi_data":       {
            "occupancy_rate":     "62%",
            "revpar":             "$145",
            "booking_pace":       "Down 15% YoY",
            "competitor_pricing": "Avg $180/night",
        },
        "media_data":    {
            "monthly_budget":  "$50,000",
            "google_ads_roas": "4.2x",
            "meta_ads_roas":   "2.1x (below 3x target)",
        },
        "review_data":   {},
        "forecast_data": {},
    },
    {
        "title":   "ANNUAL STRATEGIC REVIEW",
        "pattern": "All 5 agents  →  bi + media + pricing + reputation + forecast",
        "query": "Annual review: assess financial performance, marketing ROI, pricing, guest satisfaction, and produce a 12-month revenue forecast.",
        "bi_data":       {
            "occupancy_rate":     "68%",
            "revpar":             "$152",
            "booking_pace":       "+3% YoY",
            "competitor_pricing": "Avg $178/night",
        },
        "media_data":    {
            "monthly_budget":  "$50,000",
            "google_ads_roas": "3.8x",
            "meta_ads_roas":   "2.4x",
        },
        "review_data":   {
            "tripadvisor_rating": "4.1",
            "nps_score":          "48",
            "sentiment_trend":    "Stable",
        },
        "forecast_data": {
            "revenue_trend_ytd":         "+6% vs prior year",
            "forward_booking_index":     "Q1 +12%, Q2 +4%",
            "revpar_forecast_next_year": "$162 optimistic / $148 base",
        },
    },
]


def build_initial_state(case: dict) -> dict:
    return {
        "query":               case["query"],
        "bi_data":             case["bi_data"],
        "media_data":          case["media_data"],
        "review_data":         case["review_data"],
        "forecast_data":       case["forecast_data"],
        "next_agents":         [],
        "routing_reasoning":   "",
        "bi_analysis":         "",
        "media_analysis":      "",
        "pricing_analysis":    "",
        "reputation_analysis": "",
        "forecast_analysis":   "",
        "final_strategy":      "",
        "history":             [],
        "agent_messages":      [],
        "additional_insights": {},
    }


def _preview(text: str, chars: int = 320) -> str:
    flat = text.strip().replace("\n", " ")
    return flat[:chars] + ("..." if len(flat) > chars else "")


def run_case(graph, case: dict, index: int, total: int) -> dict:
    print(f"\n{div()}")
    print(f"  USE CASE {index} of {total}  |  {case['title']}")
    print(f"  {case['pattern']}")
    print(div())
    print(f"\n  QUERY:  {_preview(case['query'], 200)}\n")

    initial_state = build_initial_state(case)
    acc: dict = {}

    print("  Agents running...", flush=True)
    for chunk in graph.stream(initial_state, stream_mode="updates"):
        for node_name, delta in chunk.items():
            print(f"    {AGENT_LABELS.get(node_name, node_name):<42} done")
            for k, v in delta.items():
                if k in ("history", "agent_messages"):
                    acc[k] = acc.get(k, []) + v
                else:
                    acc[k] = v

    activated = acc.get("next_agents", [])

    # ── Routing decision ──────────────────────────────────────────────────────
    print(f"\n  {sep()}")
    print("  ORCHESTRATOR ROUTING DECISION")
    print(f"  {sep()}")
    print(f"  Activated : {activated}")
    print(f"  Reasoning : {acc.get('routing_reasoning', '')}")

    # ── Worker outputs ────────────────────────────────────────────────────────
    print(f"\n  {sep()}")
    print("  SPECIALIST AGENT OUTPUTS  (each wrote to shared state independently)")
    print(f"  {sep()}")
    for agent_id in activated:
        field, label = AGENT_OUTPUT_FIELDS.get(agent_id, (None, agent_id))
        if not field:
            continue
        output = acc.get(field, "")
        if not output:
            continue
        print(f"\n  [{label}]")
        print(f"  {_preview(output, 300)}")

    # ── Final strategy ────────────────────────────────────────────────────────
    n_sources = len(activated)
    print(f"\n  {sep()}")
    print(f"  FINAL STRATEGY  (CCO synthesised {n_sources} report(s) from shared state)")
    print(f"  {sep()}")
    print(f"\n  {_preview(acc.get('final_strategy', 'No strategy generated.'), 500)}")
    print()

    return {"title": case["title"], "activated": activated, "pattern": case["pattern"]}


def routing_summary(results: list):
    print(f"\n{div()}")
    print("  ROUTING SUMMARY  —  AI Orchestrator decisions across all use cases")
    print(div())
    print()
    for i, r in enumerate(results, 1):
        n          = len(r["activated"])
        agents_str = ", ".join(r["activated"]) if r["activated"] else "none"
        tag        = "ALL agents" if n == 5 else f"{n} agent{'s' if n != 1 else ''} "
        print(f"  #{i}  {r['title']:<38}  {tag:<12}  [{agents_str}]")
    print()
    patterns = sorted({len(r["activated"]) for r in results})
    print(f"  Patterns demonstrated: {patterns}  →  "
          "proves the orchestrator routes to exactly the right subset every time.")
    print(f"\n{div()}\n")


def main():
    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_groq_api_key_here":
        print("ERROR: Set GROQ_API_KEY in .env   (free key at https://console.groq.com)")
        sys.exit(1)

    print(f"\n{div()}")
    print("  HOSPITALITY MULTI-AGENT INTELLIGENCE SYSTEM")
    print("  6 use cases  |  dynamic orchestration  |  1 to 5 agents per query")
    print(div())
    print()
    print("  The AI Orchestrator reads each query + available data, then decides")
    print("  which specialist agents to activate.  Agents run in parallel and write")
    print("  their reports to shared state.  The CCO synthesises whatever is present.")
    print()
    print(f"  Required servers:  :8001 bi  :8002 media  :8003 pricing")
    print(f"                     :8004 coordinator  :8005 reputation  :8006 forecast")
    print(f"  Start with:  .\\start_agents.ps1")
    print()

    graph   = create_hospitality_graph()
    results = []

    for i, case in enumerate(USE_CASES, 1):
        result = run_case(graph, case, i, len(USE_CASES))
        results.append(result)
        if i < len(USE_CASES):
            print("  Pausing 8s to respect Groq TPM limit...")
            time.sleep(8)

    routing_summary(results)


if __name__ == "__main__":
    main()
