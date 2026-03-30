import os
import urllib.request
import uuid

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from src.graph import create_hospitality_graph

load_dotenv()

_AGENT_PORTS = [8001, 8002, 8003, 8004, 8005, 8006]


def _agents_ready() -> list[int]:
    """Return list of ports that are NOT responding."""
    down = []
    for port in _AGENT_PORTS:
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/ok", timeout=2)
        except Exception:
            down.append(port)
    return down


mcp = FastMCP("Hospitality Agent System")


@mcp.tool()
def run_hospitality_analysis(
    query: str,
    bi_occupancy_rate: str = "N/A",
    bi_revpar: str = "N/A",
    bi_booking_pace: str = "N/A",
    bi_cancellation_rate: str = "N/A",
    bi_competitor_pricing: str = "N/A",
    media_budget: str = "N/A",
    media_google_roas: str = "N/A",
    media_meta_roas: str = "N/A",
    media_campaign_focus: str = "N/A",
    media_website_conversion_rate: str = "N/A",
    review_tripadvisor_rating: str = "N/A",
    review_google_rating: str = "N/A",
    review_nps_score: str = "N/A",
    review_sentiment_trend: str = "N/A",
    forecast_revenue_trend_ytd: str = "N/A",
    forecast_market_growth_rate: str = "N/A",
    forecast_forward_booking_index: str = "N/A",
    forecast_revpar_next_year: str = "N/A",
) -> str:
    """
    Run the multi-agent hospitality analysis.

    The orchestrator automatically activates only the agents whose domain matches
    the query AND whose data fields are non-empty. You do not need to provide all
    parameters — supply only what is relevant to your scenario.

    Requires all 6 agent servers running (start_agents.ps1).

    Args:
        query: The business question or goal for the agents
        bi_occupancy_rate: Current occupancy rate (e.g., "62%")
        bi_revpar: Revenue Per Available Room (e.g., "$145")
        bi_booking_pace: YoY booking pace (e.g., "Down 15% YoY")
        bi_cancellation_rate: Cancellation rate (e.g., "12%")
        bi_competitor_pricing: Competitor avg price (e.g., "Avg $180/night")
        media_budget: Monthly marketing budget (e.g., "$50,000")
        media_google_roas: Google Ads ROAS (e.g., "4.2x")
        media_meta_roas: Meta Ads ROAS (e.g., "2.1x")
        media_campaign_focus: Current campaign focus (e.g., "Brand Awareness")
        media_website_conversion_rate: Website CVR (e.g., "1.8%")
        review_tripadvisor_rating: TripAdvisor score (e.g., "4.1")
        review_google_rating: Google rating (e.g., "4.3")
        review_nps_score: Net Promoter Score (e.g., "48")
        review_sentiment_trend: Trend description (e.g., "Stable")
        forecast_revenue_trend_ytd: YTD revenue trend (e.g., "+6%")
        forecast_market_growth_rate: Market growth rate (e.g., "3.2%")
        forecast_forward_booking_index: Forward demand (e.g., "Q1 +12%")
        forecast_revpar_next_year: RevPAR forecast (e.g., "$162 optimistic")
    """
    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_groq_api_key_here":
        return "ERROR: GROQ_API_KEY not configured."

    down = _agents_ready()
    if down:
        return (
            f"ERROR: Agent servers not reachable on ports {down}. "
            "Run .\\start_agents.ps1 first and wait for all 6 servers to show 'Ready'."
        )

    graph = create_hospitality_graph()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    # Build data dicts — only include fields that were actually provided
    bi_data: dict = {}
    if any(v != "N/A" for v in [
        bi_occupancy_rate, bi_revpar, bi_booking_pace,
        bi_cancellation_rate, bi_competitor_pricing,
    ]):
        bi_data = {k: v for k, v in {
            "occupancy_rate":     bi_occupancy_rate,
            "revpar":             bi_revpar,
            "booking_pace":       bi_booking_pace,
            "cancellation_rate":  bi_cancellation_rate,
            "competitor_pricing": bi_competitor_pricing,
        }.items() if v != "N/A"}

    media_data: dict = {}
    if any(v != "N/A" for v in [
        media_budget, media_google_roas, media_meta_roas,
        media_campaign_focus, media_website_conversion_rate,
    ]):
        media_data = {k: v for k, v in {
            "monthly_budget":          media_budget,
            "google_ads_roas":         media_google_roas,
            "meta_ads_roas":           media_meta_roas,
            "campaign_focus":          media_campaign_focus,
            "website_conversion_rate": media_website_conversion_rate,
        }.items() if v != "N/A"}

    review_data: dict = {}
    if any(v != "N/A" for v in [
        review_tripadvisor_rating, review_google_rating,
        review_nps_score, review_sentiment_trend,
    ]):
        review_data = {k: v for k, v in {
            "tripadvisor_rating": review_tripadvisor_rating,
            "google_rating":      review_google_rating,
            "nps_score":          review_nps_score,
            "sentiment_trend":    review_sentiment_trend,
        }.items() if v != "N/A"}

    forecast_data: dict = {}
    if any(v != "N/A" for v in [
        forecast_revenue_trend_ytd, forecast_market_growth_rate,
        forecast_forward_booking_index, forecast_revpar_next_year,
    ]):
        forecast_data = {k: v for k, v in {
            "revenue_trend_ytd":         forecast_revenue_trend_ytd,
            "market_growth_rate":        forecast_market_growth_rate,
            "forward_booking_index":     forecast_forward_booking_index,
            "revpar_forecast_next_year": forecast_revpar_next_year,
        }.items() if v != "N/A"}

    initial_state = {
        "query":               query,
        "bi_data":             bi_data,
        "media_data":          media_data,
        "review_data":         review_data,
        "forecast_data":       forecast_data,
        "next_agents":         [],
        "routing_reasoning":   "",
        "bi_analysis":         "",
        "media_analysis":      "",
        "pricing_analysis":    "",
        "reputation_analysis": "",
        "forecast_analysis":   "",
        "final_strategy":      "",
        "agent_messages":      [],
    }

    try:
        final_state = graph.invoke(initial_state, config=config)

        sections = [
            "=== ORCHESTRATOR ROUTING ===",
            f"Agents activated : {', '.join(final_state.get('next_agents', []))}",
            f"Reasoning        : {final_state.get('routing_reasoning', 'N/A')}",
        ]
        analysis_fields = [
            ("BI ANALYSIS",         "bi_analysis"),
            ("MEDIA ANALYSIS",      "media_analysis"),
            ("PRICING ANALYSIS",    "pricing_analysis"),
            ("REPUTATION ANALYSIS", "reputation_analysis"),
            ("FORECAST ANALYSIS",   "forecast_analysis"),
            ("FINAL STRATEGY",      "final_strategy"),
        ]
        for label, field in analysis_fields:
            value = final_state.get(field, "")
            if value.strip():
                sections += [f"\n=== {label} ===", value]

        return "\n".join(sections)
    except Exception as e:
        return f"ERROR running analysis: {e}"


if __name__ == "__main__":
    mcp.run()
