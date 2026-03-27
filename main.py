import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.graph import create_hospitality_graph

def main():
    """
    Main execution entry point.
    Demonstrates how to run the multi-agent graph with mock hospitality data.
    """
    load_dotenv()
    
    if not os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") == "your_google_api_key_here":
        print("ERROR: Please set your GOOGLE_API_KEY in the .env file.")
        print("You can get one at: https://aistudio.google.com/app/apikey")
        sys.exit(1)

    print("Initializing Multi-Agent Hospitality Graph...")
    graph = create_hospitality_graph()

    # Mock Data representing current state of the business
    bi_data = {
        "current_month": "October",
        "occupancy_rate": "62%",  # Low occupancy
        "revpar": "$145",
        "booking_pace": "Down 15% YoY for Q4",
        "cancellation_rate": "12% (Stable)",
        "competitor_pricing": "Average $180/night"
    }

    media_data = {
        "monthly_budget": "$50,000",
        "google_ads_roas": "4.2x",
        "meta_ads_roas": "2.1x",
        "campaign_focus": "Brand Awareness (Global)",
        "website_conversion_rate": "1.8%"
    }

    # Initial state
    initial_state = {
        "query": "We have low occupancy projected for Q4. How should we adjust our pricing and marketing spend to maximize revenue?",
        "bi_data": bi_data,
        "media_data": media_data,
        "bi_analysis": "",
        "media_analysis": "",
        "final_strategy": "",
        "history": [],
        "additional_insights": {}
    }

    print("\nStarting execution flow...\n")
    
    # Run the graph
    # Using stream allows us to observe the output of each node as it executes
    final_state = None
    for output in graph.stream(initial_state):
        # The output is a dict where the key is the node name that just ran
        for node_name, state_update in output.items():
            print(f"--- Completed Node: {node_name} ---")
            # Keep track of the latest state
            final_state = state_update

    # At this point, the graph has finished executing.
    # In a real app, you would retrieve this from the checkpointer database.
    
    print("\n==================================================")
    print("FINAL STRATEGY FROM CCO AGENT:")
    print("==================================================\n")
    
    # We need to print the final strategy from the actual final state 
    # (The stream yields partial state updates, so we need to collect them or just invoke directly)
    
    print("To get the full final aggregated state, we can also use graph.invoke().")
    print("Running full invoke to demonstrate final output aggregation...\n")
    
    final_full_state = graph.invoke(initial_state)
    
    print(final_full_state.get("final_strategy", "No strategy generated."))
    print("\n==================================================")
    print("EXECUTION HISTORY:")
    for step in final_full_state.get("history", []):
        print(f"- {step}")
    
    print("\nScalability check - Extra Agent Insights:")
    for agent, insight in final_full_state.get("additional_insights", {}).items():
        print(f"[{agent}]: Exists in state.")

if __name__ == "__main__":
    main()
