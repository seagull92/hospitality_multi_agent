"""
Revenue Forecast Agent — deployed on pod :8006

READS : query, bi_data, forecast_data
WRITES: forecast_analysis

Pod isolation: this file contains ONLY the revenue_forecast_agent implementation.
bi_data provides the historical baseline; forecast_data provides forward-looking indicators.
Both are required inputs for a credible 12-month revenue forecast.
"""
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

_llm = init_chat_model("groq:llama-3.1-8b-instant", temperature=0.2, max_tokens=400)

_SYSTEM_PROMPT = (
    "You are a Revenue Forecasting Analyst for a hospitality group. "
    "Using the provided historical BI performance data and forward-looking market indicators, "
    "build a revenue forecast with specific numerical projections, seasonality insights, "
    "and strategic recommendations for the next 12 months."
)


def revenue_forecast_agent(state: dict) -> dict:
    bi_data = state.get("bi_data", {})
    forecast_data = state.get("forecast_data", {})
    query = state.get("query", "")

    if not forecast_data:
        return {"forecast_analysis": "No forecast data provided — analysis skipped."}

    response = _llm.invoke([
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Goal: {query}\n\n"
                f"Historical BI Data:\n{bi_data}\n\n"
                f"Forward-Looking Indicators:\n{forecast_data}"
            )
        ),
    ])
    return {"forecast_analysis": response.content}
