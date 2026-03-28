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
                          │              │               │    (Command pattern)
                          │    ┌─────────┼─────────┐     │
                          │    ▼         ▼         ▼     │
                          │  :8001     :8002     :8003   │  ← RemoteGraph HTTP calls
                          │ bi_analyzer media  pricing   │
                          │    └─────────┼─────────┘     │
                          │             ▼                 │
                          │        :8004 coordinator      │  ← RemoteGraph HTTP call
                          │             │                 │
                          │           END                 │
                          └──────────────────────────────┘
```

### Agents

| Agent | Port | Role |
|---|---|---|
| `bi_analyzer` | 8001 | Analyzes occupancy, RevPAR, booking pace |
| `media_analyzer` | 8002 | Evaluates ad spend, ROAS, channel performance |
| `pricing_optimizer` | 8003 | Recommends rate adjustments and revenue strategy |
| `strategy_coordinator` | 8004 | CCO — synthesizes all three into a final strategy |

### Key design decisions

- **Blackboard pattern** — agents never call each other directly; all communication is through `AgentState` (shared state over HTTP JSON)
- **Parallel fan-out** — bi, media, and pricing agents run simultaneously via `Command` goto
- **State reducers** — `_keep_nonempty`, `_merge_dicts`, `operator.add` prevent parallel write conflicts
- **RemoteGraph exclusively** — no in-process fallback; forces true microservice separation

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

### 3. Start all 4 agent servers
```powershell
.\start_agents.ps1
```
This opens 4 terminal windows, each running `langgraph dev` on its own port. Wait for all to show `Ready`.

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
│   └── coordinator/   server.py + langgraph.json  → port 8004
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
