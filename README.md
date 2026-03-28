# Hospitality Multi-Agent Intelligence System

A production-ready multi-agent system built with **LangGraph**, **Groq (Llama 3.3 70B)**, and **RemoteGraph** — where every specialist agent runs as an independent HTTP microservice and communicates exclusively through shared state.

---

## Architecture

```
                          ┌─────────────────────────────────────────┐
                          │           main.py / MCP tool            │
                          └──────────────┬──────────────────────────┘
                                         │  invoke(initial_state)
                                         ▼
                          ┌──────────────────────────────┐
                          │   src/graph.py  (StateGraph) │
                          │                              │
                          │   START → orchestrator       │  ← in-process LLM router
                          │              │               │    (Command pattern,
                          │    ┌─────────┼──────────┐    │     1 to 5 workers)
                          │    ▼         ▼          ▼    │
                          │  :8001     :8002      :8003  │  ← RemoteGraph HTTP
                          │ bi_anal.  media     pricing  │
                          │              :8005    :8006  │
                          │           reputa.  forecast  │
                          │    └─────────┼──────────┘    │
                          │             ▼                 │
                          │     :8004 coordinator         │  ← RemoteGraph HTTP
                          │             │                 │
                          │           END                 │
                          └──────────────────────────────┘
```

### Agents

| Agent | Port | Data it reads | Writes to |
|---|---|---|---|
| `bi_analyzer` | 8001 | `bi_data` | `bi_analysis` |
| `media_analyzer` | 8002 | `media_data` | `media_analysis` |
| `pricing_optimizer` | 8003 | `bi_data` (pricing context) | `pricing_analysis` |
| `strategy_coordinator` | 8004 | all analysis fields | `final_strategy` |
| `reputation_agent` | 8005 | `review_data` | `reputation_analysis` |
| `revenue_forecast_agent` | 8006 | `bi_data` + `forecast_data` | `forecast_analysis` |

### Key design decisions

- **Dynamic routing** — orchestrator activates only agents whose required data is non-empty; 1 to 5 workers per query
- **Blackboard pattern** — agents never call each other; all communication is JSON over HTTP through `AgentState`
- **Parallel fan-out** — selected workers run simultaneously via `Command(goto=[...])`
- **State reducers** — `_keep_nonempty`, `_merge_dicts`, `operator.add` prevent parallel write conflicts
- **RemoteGraph exclusively** — no in-process fallback; every agent is a true independent microservice

### Use cases demonstrating routing patterns

| # | Scenario | Agents activated |
|---|---|---|
| 1 | Marketing channel crisis | 1 — `media_analyzer` |
| 2 | Competitor rate war | 1 — `pricing_optimizer` |
| 3 | Q4 revenue shortfall | 2 — `bi_analyzer` + `pricing_optimizer` |
| 4 | Guest reputation crisis | 2 — `reputation_agent` + `media_analyzer` |
| 5 | Q4 full commercial strategy | 3 — `bi` + `media` + `pricing` |
| 6 | Annual strategic review | 5 — all agents |

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
Copy `.env.example` to `.env` and fill in your keys:
```bash
copy .env.example .env
```

Required:
- `GROQ_API_KEY` — free at [console.groq.com](https://console.groq.com)

Optional (for LangSmith run tracing):
- `LANGSMITH_API_KEY` — free personal key at [smith.langchain.com](https://smith.langchain.com)
- `LANGCHAIN_TRACING_V2=true`
- `LANGCHAIN_PROJECT=hospitality-multi-agent`

### 3. Start all 6 agent servers
```powershell
.\start_agents.ps1
```
This opens 6 terminal windows (ports 8001–8006), each running `langgraph dev`. Wait for all to show `Ready`.

### 4. Run the demo
```bash
python main.py
```

---

## MCP Tool (Windsurf / Claude Desktop)

`mcp_server.py` exposes the entire pipeline as a single MCP tool — callable directly from any MCP-compatible AI assistant without touching the terminal.

The tool `run_hospitality_analysis` is registered in `.windsurf/mcp.json`. Agent servers must be running first.

---

## Project Structure

```
hospitality_multi_agent/
├── agents/
│   ├── bi/            server.py + langgraph.json  → port 8001
│   ├── media/         server.py + langgraph.json  → port 8002
│   ├── pricing/       server.py + langgraph.json  → port 8003
│   ├── coordinator/   server.py + langgraph.json  → port 8004
│   ├── reputation/    server.py + langgraph.json  → port 8005
│   └── forecast/      server.py + langgraph.json  → port 8006
├── src/
│   ├── state.py       AgentState TypedDict with reducers
│   ├── orchestrator.py  LLM router (Command pattern)
│   ├── agents.py      Agent functions (bi, media, pricing, coordinator)
│   └── graph.py       StateGraph wiring all RemoteGraph nodes
├── main.py            CLI entrypoint with formatted management report
├── mcp_server.py      FastMCP tool wrapper
├── start_agents.ps1   Launches all 4 servers in separate terminals
├── langgraph.json     Root config (for langgraph dev on the orchestrator)
└── .env               API keys (gitignored)
```
