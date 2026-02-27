import time
import schedule
import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - SCHEDULER - %(message)s')

def run_live_pipeline():
    logging.info("Triggering pipeline_market_data.py --live ...")
    try:
        # Run the pipeline script
        result = subprocess.run(["python", "iposhala_test/scripts/pipeline_market_data.py", "--live"], capture_output=True, text=True)
        if result.returncode == 0:
            logging.info("Live pipeline executed successfully.")
        else:
            logging.error(f"Live pipeline failed with exit code {result.returncode}")
            logging.error(result.stderr)
    except Exception as e:
        logging.error(f"Error executing live pipeline: {str(e)}")

def run_gmp_pipeline():
    logging.info("Triggering pipeline_gmp.py ...")
    try:
        result = subprocess.run(["python", "iposhala_test/scripts/pipeline_gmp.py"], capture_output=True, text=True)
        if result.returncode == 0:
            logging.info("GMP pipeline executed successfully.")
        else:
            logging.error(f"GMP pipeline failed with exit code {result.returncode}")
            logging.error(result.stderr)
    except Exception as e:
        logging.error(f"Error executing GMP pipeline: {str(e)}")

def main():
    logging.info("Starting IPOshala background scheduler...")
    
    # Run once immediately on startup
    run_live_pipeline()
    run_gmp_pipeline()
    
    # Schedule to run every hour
    schedule.every(1).hours.do(run_live_pipeline)
    
    # Schedule GMP every 30 mins
    schedule.every(30).minutes.do(run_gmp_pipeline)
    
    logging.info("Scheduler loop active. Press Ctrl+C to exit.")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60) # Only check every minute to save CPU
        except KeyboardInterrupt:
            logging.info("Scheduler shutting down...")
            break
        except Exception as e:
            logging.error(f"Scheduler error: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()
