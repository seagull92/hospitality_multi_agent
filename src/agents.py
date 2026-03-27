import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Ensure we have our environment setup
load_dotenv()

# We use the new google-genai SDK models via LangChain's wrapper
# For complex reasoning tasks, gemini-2.5-pro or gemini-2.0-flash are excellent.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.2, 
    max_output_tokens=2048
)

def bi_agent(state):
    """
    Business Intelligence Agent: Analyzes occupancy rates, RevPAR, and booking windows.
    """
    print("--- BI AGENT EXECUTING ---")
    
    bi_data_str = str(state.get("bi_data", {}))
    query = state.get("query", "")
    
    system_prompt = (
        "You are an expert Business Intelligence Analyst for a hospitality group. "
        "Your task is to analyze the provided BI data (occupancy rates, RevPAR, booking pace, cancellations) "
        "and extract actionable insights. Focus on revenue opportunities, identifying low-performing periods, "
        "and summarizing the financial health of the properties."
    )
    
    user_prompt = f"Target Query: {query}\n\nBI Data Provided:\n{bi_data_str}"
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    return {
        "bi_analysis": response.content,
        "history": ["BI Agent Analysis Completed"]
    }

def media_agent(state):
    """
    Media & Marketing Agent: Analyzes ad spend, ROAS, and channel performance.
    """
    print("--- MEDIA AGENT EXECUTING ---")
    
    media_data_str = str(state.get("media_data", {}))
    query = state.get("query", "")
    
    system_prompt = (
        "You are an expert Media & Performance Marketing Director for a hospitality group. "
        "Your task is to analyze the provided Media data (Ad spend, ROAS by channel, CTR, CPA) "
        "and determine how marketing dollars are currently performing and where they should be reallocated."
    )
    
    user_prompt = f"Target Query: {query}\n\nMedia Data Provided:\n{media_data_str}"
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    return {
        "media_analysis": response.content,
        "history": ["Media Agent Analysis Completed"]
    }

def strategy_coordinator_agent(state):
    """
    Strategy Coordinator Agent: Combines BI and Media insights into a cohesive action plan.
    This acts as the orchestrator/synthesizer in the architecture.
    """
    print("--- STRATEGY COORDINATOR AGENT EXECUTING ---")
    
    bi_analysis = state.get("bi_analysis", "")
    media_analysis = state.get("media_analysis", "")
    query = state.get("query", "")
    
    # Scalability: Incorporate insights from any new N agents added to the graph
    additional_insights = state.get("additional_insights", {})
    extra_insights_str = ""
    for agent_name, insight in additional_insights.items():
        extra_insights_str += f"\n\n{agent_name.capitalize()} Insights:\n{insight}"
    
    system_prompt = (
        "You are the Chief Commercial Officer (CCO) of a hospitality group. "
        "Your task is to review the independent analyses from your Business Intelligence team "
        "and your Media/Marketing team, and synthesize them into a cohesive, actionable business strategy. "
        "If BI identifies a low-occupancy period, how should Media adjust? If Media has high ROAS but BI shows low RevPAR, why?"
    )
    
    user_prompt = (
        f"Original Goal: {query}\n\n"
        f"Business Intelligence Analysis:\n{bi_analysis}\n\n"
        f"Media & Marketing Analysis:\n{media_analysis}\n"
        f"{extra_insights_str}"
    )
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    return {
        "final_strategy": response.content,
        "history": ["Strategy Coordinator Synthesis Completed"]
    }

# --- EXAMPLE OF SCALABILITY: ADDING N MORE AGENTS ---
def pricing_agent(state):
    """
    An example of how easy it is to add a new specialized agent (e.g., dynamic pricing).
    """
    print("--- PRICING AGENT EXECUTING ---")
    
    bi_analysis = state.get("bi_analysis", "")
    query = state.get("query", "")
    
    system_prompt = (
        "You are a Revenue Management & Pricing Specialist. Based on the BI analysis, "
        "recommend specific percentage price adjustments for upcoming periods."
    )
    
    user_prompt = f"Goal: {query}\n\nBI Context:\n{bi_analysis}"
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    current_insights = state.get("additional_insights", {})
    current_insights["pricing_agent"] = response.content
    
    return {
        "additional_insights": current_insights,
        "history": ["Pricing Agent Recommendations Generated"]
    }
