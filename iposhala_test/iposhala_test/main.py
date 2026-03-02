import os
import sys
import argparse
import uvicorn
import logging

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the FastAPI app from the active server module
from iposhala_test.api.server import app

# Import pipeline functions
from iposhala_test.scripts.pipeline_documents import ingest_documents_from_csv
from iposhala_test.scripts.pipeline_company_info import fetch_and_save_logos, generate_and_save_descriptions, fetch_and_save_shareholding
from iposhala_test.scripts.pipeline_market_data import fetch_live_ipos, fetch_all_nse_data
from iposhala_test.scripts.pipeline_historical import run_historical_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')

def run_all_pipelines():
    """Run all data extraction pipelines sequentially."""
    print("========================================")
    print("🚀 STARTING MASTER DATA PIPELINE EXECUTION")
    print("========================================")
    
    # 1. Documents Pipeline
    print("\n--- 1. Running Documents Pipeline ---")
    try:
        ingest_documents_from_csv()
    except Exception as e:
        print(f"Error: {e}")

    # 2. Company Info Pipeline
    print("\n--- 2. Running Company Info Pipeline ---")
    try:
        fetch_and_save_logos()
        generate_and_save_descriptions()
        fetch_and_save_shareholding()
    except Exception as e:
        print(f"Error: {e}")

    # 3. Market Data Pipeline
    print("\n--- 3. Running Market Data Pipeline ---")
    try:
        fetch_live_ipos()
        fetch_all_nse_data()
    except Exception as e:
        print(f"Error: {e}")

    # 4. Historical Data Pipeline
    print("\n--- 4. Running Historical Data Pipeline ---")
    try:
        run_historical_pipeline()
    except Exception as e:
        print(f"Error: {e}")

    # 5. Financials Pipeline
    print("\n--- 5. Running Financials Pipeline ---")
    # Execute the financials script directly to avoid argparse conflicts with main.py
    try:
        script_path = os.path.join(os.path.dirname(__file__), "scripts", "pipeline_financials.py")
        os.system(f'"{sys.executable}" "{script_path}"')
    except Exception as e:
        print(f"Error: {e}")

    print("\n========================================")
    print("✅ MASTER PIPELINE EXECUTION COMPLETE")
    print("========================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Iposhala Main Entrypoint - Server and Pipelines")
    parser.add_argument("--run-pipelines", action="store_true", help="Run all data pipelines and exit")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the API server on")
    
    # Parse known args so uvicorn doesn't fail if other arbitrary args are passed
    args, unknown = parser.parse_known_args()
    
    if args.run_pipelines:
        run_all_pipelines()
    else:
        # Run the server
        uvicorn.run("iposhala_test.api.server:app", host="0.0.0.0", port=args.port, reload=True)
