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
    Main loop to run the stats.

    Args:
        interval_seconds (int): The time interval (in seconds) between each run.
    """
    load_dotenv('.env')
    conn_string = os.getenv("CONN_STRING")

    if not conn_string:
        print("ERROR: CONN_STRING is not set in the environment. Cannot proceed.")
        return

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
