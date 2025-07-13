import os
import asyncio
import time
from dotenv import load_dotenv
import sys

from operations.stats_monitor import get_pc_stats, insert_stats_to_db
from database.engine import init_db

async def gather_stats_pipeline():
    """
    Gathers PC and GPU statistics and inserts them into the database.
    Handles errors gracefully.
    """
    try:
        stats_list = get_pc_stats()
        if stats_list:
            await insert_stats_to_db(stats_list)
            print("Stats gathered and inserted successfully.")
            sys.stdout.flush() # Ensure print is visible immediately
        else:
            print("Failed to gather stats. No data to insert.")
            sys.stdout.flush() # Ensure print is visible immediately
    except Exception as e:
        print(f"An error occurred during the stats gathering pipeline: {e}")
        sys.stdout.flush() # Ensure print is visible immediately
        # import traceback
        # traceback.print_exc()


async def main_loop(interval_seconds: int = 10):
    """
    Main loop to run the stats gathering pipeline periodically.

    Args:
        interval_seconds (int): The time interval (in seconds) between each run.
    """
    print("DEBUG: Starting main_loop...")
    sys.stdout.flush() # Ensure print is visible immediately

    load_dotenv('.env')
    print("DEBUG: .env file loaded.")
    sys.stdout.flush() # Ensure print is visible immediately

    conn_string = os.getenv("CONN_STRING")
    print(f"DEBUG: Retrieved CONN_STRING from environment: {conn_string}")
    sys.stdout.flush() # Ensure print is visible immediately

    if not conn_string:
        print("ERROR: CONN_STRING is not set in the environment. Cannot proceed.")
        sys.stdout.flush() # Ensure print is visible immediately
        return # Exit if connection string is missing

    try:
        print("DEBUG: Calling init_db...")
        sys.stdout.flush() # Ensure print is visible immediately
        await init_db(conn_string)
        print("DEBUG: init_db completed successfully.")
        sys.stdout.flush() # Ensure print is visible immediately

        while True:
            await gather_stats_pipeline()
            await asyncio.sleep(interval_seconds)
    except asyncio.CancelledError:
        print("\nPC Stats monitoring stopped by user.")
        sys.stdout.flush() # Ensure print is visible immediately
    except Exception as e:
        print(f"\nAn unexpected error occurred in the main loop: {e}")
        sys.stdout.flush() # Ensure print is visible immediately
        # import traceback
        # traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main_loop(10))
