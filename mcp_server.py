from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

from src.graph import create_hospitality_graph

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Hospitality Agent System")

@mcp.tool()
def run_hospitality_analysis(
    query: str,
    bi_occupancy_rate: str,
    bi_revpar: str,
    media_budget: str,
    media_roas: str
) -> str:
    """
    Run the multi-agent hospitality analysis given BI and Media metrics.
    
    Args:
        query: The main goal or question for the agents
        bi_occupancy_rate: Current occupancy rate (e.g., "62%")
        bi_revpar: Current Revenue Per Available Room (e.g., "$145")
        media_budget: Current marketing budget (e.g., "$50,000")
        media_roas: Current Return on Ad Spend (e.g., "4.2x")
    """
    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_groq_api_key_here":
        return "ERROR: Groq API Key is not configured. Please set GROQ_API_KEY."

    graph = create_hospitality_graph()

    bi_data = {
        "occupancy_rate": bi_occupancy_rate,
        "revpar": bi_revpar,
    }

    media_data = {
        "monthly_budget": media_budget,
        "roas": media_roas,
    }

    initial_state = {
        "query": query,
        "bi_data": bi_data,
        "media_data": media_data,
        "next_agents": [],
        "routing_reasoning": "",
        "bi_analysis": "",
        "media_analysis": "",
        "final_strategy": "",
        "history": [],
        "additional_insights": {}
    }

    try:
        final_state = graph.invoke(initial_state)
        
        result = [
            f"=== ORCHESTRATOR ROUTING ===",
            f"Agents activated: {', '.join(final_state.get('next_agents', []))}",
            f"Reasoning: {final_state.get('routing_reasoning', 'N/A')}",
            "\n=== BI ANALYSIS ===",
            final_state.get("bi_analysis", "N/A"),
            "\n=== MEDIA ANALYSIS ===",
            final_state.get("media_analysis", "N/A"),
            "\n=== FINAL STRATEGY ===",
            final_state.get("final_strategy", "N/A")
        ]
        
        return "\n".join(result)
    except Exception as e:
        return f"Error running analysis: {str(e)}"

if __name__ == "__main__":
    mcp.run()
