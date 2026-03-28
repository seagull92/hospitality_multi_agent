import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.graph import create_hospitality_graph

# ── Formatting helpers ────────────────────────────────────────────────────────
W = 68
def div(char="="): return char * W
def section(title): print(f"\n{div()}\n  {title}\n{div()}")
def sep():          print(div("-"))

# Human-readable names for internal agent IDs
AGENT_LABELS = {
    "orchestrator":        "AI Orchestrator",
    "bi_analyzer":         "Business Intelligence Analyst",
    "media_analyzer":      "Media & Marketing Director",
    "pricing_optimizer":   "Revenue & Pricing Specialist",
    "strategy_coordinator":"Chief Commercial Officer (CCO)",
}


def main():
    load_dotenv()

    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_groq_api_key_here":
        print("ERROR: Please set your GROQ_API_KEY in the .env file.")
        print("Get one free at: https://console.groq.com")
        sys.exit(1)

    graph = create_hospitality_graph()

    bi_data = {
        "occupancy_rate":     "62%",
        "revpar":             "$145",
        "booking_pace":       "Down 15% YoY for Q4",
        "cancellation_rate":  "12% (Stable)",
        "competitor_pricing": "Avg $180/night",
    }
    media_data = {
        "monthly_budget":          "$50,000",
        "google_ads_roas":         "4.2x",
        "meta_ads_roas":           "2.1x",
        "campaign_focus":          "Brand Awareness (Global)",
        "website_conversion_rate": "1.8%",
    }
    query = (
        "We have low occupancy projected for Q4. "
        "How should we adjust pricing and marketing spend to maximize revenue?"
    )

    initial_state = {
        "query":             query,
        "bi_data":           bi_data,
        "media_data":        media_data,
        "next_agents":       [],
        "routing_reasoning": "",
        "bi_analysis":       "",
        "media_analysis":    "",
        "final_strategy":    "",
        "history":           [],
        "agent_messages":    [],
        "additional_insights": {},
    }

    # ── Header ────────────────────────────────────────────────────────────────
    section("HOSPITALITY INTELLIGENCE REPORT  |  AI Multi-Agent System")
    print(f"\n  BUSINESS QUESTION")
    print(f"  {query}")
    print(f"\n  INPUT DATA")
    print(f"  Business  :  Occupancy {bi_data['occupancy_rate']}  |  RevPAR {bi_data['revpar']}  "
          f"|  Booking pace {bi_data['booking_pace']}")
    print(f"  Marketing :  Budget {media_data['monthly_budget']}  "
          f"|  Google ROAS {media_data['google_ads_roas']}  "
          f"|  Meta ROAS {media_data['meta_ads_roas']}")

    # ── Run the graph (single pass) ───────────────────────────────────────────
    print(f"\n{div('-')}")
    print("  RUNNING ANALYSIS ...  (agents working in parallel)")
    sep()

    acc: dict = dict(initial_state)
    acc["history"] = []
    acc["agent_messages"] = []
    node_order: list = []

    for chunk in graph.stream(initial_state, stream_mode="updates"):
        for node_name, delta in chunk.items():
            node_order.append(node_name)
            label = AGENT_LABELS.get(node_name, node_name)
            print(f"  {label:<40} done")
            for k, v in delta.items():
                if k in ("history", "agent_messages"):
                    acc[k] = acc.get(k, []) + v
                else:
                    acc[k] = v

    # ── Section 1: Orchestrator decision ─────────────────────────────────────
    section("STEP 1  |  ORCHESTRATOR DECISION")
    activated = [AGENT_LABELS.get(a, a) for a in acc.get("next_agents", [])]
    print(f"\n  The AI Orchestrator read the business question and decided to activate:\n")
    for i, name in enumerate(activated, 1):
        print(f"    {i}. {name}")
    print(f"\n  Reason: {acc.get('routing_reasoning', '')}")

    # ── Section 2: Agent inputs and outputs ───────────────────────────────────
    section("STEP 2  |  PARALLEL ANALYSIS  (all agents ran simultaneously)")

    workers = [n for n in node_order if n not in ("orchestrator", "strategy_coordinator")]

    agent_io = {
        "bi_analyzer": {
            "role":    "Analyzed business performance data",
            "input":   f"Occupancy {bi_data['occupancy_rate']}  |  RevPAR {bi_data['revpar']}  |  "
                       f"Booking pace {bi_data['booking_pace']}",
            "output":  acc.get("bi_analysis", ""),
            "out_key": "BI Analysis report",
        },
        "media_analyzer": {
            "role":    "Evaluated marketing channel performance",
            "input":   f"Budget {media_data['monthly_budget']}  |  "
                       f"Google ROAS {media_data['google_ads_roas']}  |  "
                       f"Meta ROAS {media_data['meta_ads_roas']}",
            "output":  acc.get("media_analysis", ""),
            "out_key": "Media Analysis report",
        },
        "pricing_optimizer": {
            "role":    "Recommended pricing adjustments",
            "input":   f"Occupancy {bi_data['occupancy_rate']}  |  RevPAR {bi_data['revpar']}  |  "
                       f"Competitor avg {bi_data['competitor_pricing']}",
            "output":  acc.get("additional_insights", {}).get("pricing_agent", ""),
            "out_key": "Pricing Recommendations",
        },
    }

    for w in workers:
        info  = agent_io.get(w, {})
        label = AGENT_LABELS.get(w, w)
        out   = info.get("output", "")
        # First 2 lines of agent output as a preview
        preview = "  |    ".join(out.strip().splitlines()[:2]) if out else "(no output)"
        print(f"\n  {div('-')}")
        print(f"  AGENT  : {label}")
        print(f"  ROLE   : {info.get('role', '')}")
        print(f"  INPUT  : {info.get('input', '')}")
        print(f"  OUTPUT : {info.get('out_key', '')}  -->  passed to CCO")
        print(f"           \"{preview[:120]}...\"")

    # ── Section 3: Coordinator merge ─────────────────────────────────────────
    section("STEP 3  |  CCO SYNTHESIS  (how agents passed data to each other)")
    print("""
  Each agent wrote its report into shared memory.
  The CCO then read all three reports and merged them.

  Business Intelligence Analyst  -->  BI Analysis        -+
  Media & Marketing Director     -->  Media Analysis      +-->  CCO  -->  Final Strategy
  Revenue & Pricing Specialist   -->  Pricing Advice     -+

  No agent called another directly — all communication goes
  through shared state (the "blackboard" pattern).
""")

    # ── Agent communication log ───────────────────────────────────────────────
    messages = acc.get("agent_messages", [])
    if messages:
        section("AGENT COMMUNICATION LOG  (shared state reads & writes)")
        seen = set()
        for msg in messages:
            action = msg.get("action", "")
            agent  = msg.get("agent", "")
            keys   = ", ".join(msg.get("state_keys", []))
            dedup_key = (agent, action, keys)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            arrow  = "-->" if action == "WRITE" else "<--"
            label  = AGENT_LABELS.get(agent, agent)
            print(f"  {action:<5} {arrow}  [{label}]  keys: {keys}")

    # ── Final strategy ────────────────────────────────────────────────────────
    section("FINAL STRATEGIC RECOMMENDATION")
    print()
    print(acc.get("final_strategy", "No strategy generated."))
    print(f"\n{div()}\n")


if __name__ == "__main__":
    main()
