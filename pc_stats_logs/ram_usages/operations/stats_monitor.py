import psutil
import GPUtil
from typing import Dict, List, Optional, Union, Any
from database.db_interface import DBInterface
from database.models import PcStats, GpuStats
from operations.models import PcStatsCreateData, GpuStatsCreateData
import sys

gpu_interface = DBInterface(GpuStats)
pc_interface = DBInterface(PcStats)

def get_pc_stats() -> Optional[List[Dict[str, Union[float, int, None]]]]:
    """
    Gathers general PC and GPU statistics, validates both PC and GPU stats with Pydantic,
    and returns them as a single list of dictionaries suitable for direct database insertion.

    Returns:
            A list where:
            - The first element is a dictionary containing PC statistics (validated by PcStatsCreateData).
            - Subsequent elements are dictionaries for each detected GPU (validated by GpustatsCreateData).
            Returns None if a critical error occurs during data collection.
    """
    pc_data_dict = {}
    gpu_data_list = []

    print("... Starting get_pc_stats...")
    sys.stdout.flush()

    try:
        # --- Collect CPU Stats ---
        pc_data_dict['pc_usage'] = psutil.cpu_percent(interval=None) # Non-blocking call
        cpu_freq = psutil.cpu_freq()
        pc_data_dict['pc_freq'] = round(cpu_freq.current, 2) if cpu_freq else None

        # --- Collect Memory (RAM) Stats ---
        memory = psutil.virtual_memory()
        pc_data_dict['ram_usage'] = round(memory.used / (1024**3), 2) # Used RAM in GB
        pc_data_dict['ram_available'] = round(memory.available / (1024**3), 2) # Available RAM in GB

        # --- Collect Network I/O Stats ---
        net_io = psutil.net_io_counters()
        pc_data_dict['internet_receive'] = round(net_io.bytes_recv / (1024**2), 2) # Received MB
        pc_data_dict['internet_sent'] = round(net_io.bytes_sent / (1024**2), 2) # Sent MB

        # Validate with PcStatsCreateData (validation only)
        _ = PcStatsCreateData(**pc_data_dict)
        print(f"DEBUG: PC stats collected and validated: {pc_data_dict}")
        sys.stdout.flush()

        # --- Collect GPU Stats using GPUtil ---
        try:
            print("DEBUG: Attempting to retrieve GPU stats using GPUtil...")
            sys.stdout.flush()
            gpus = GPUtil.getGPUs()
            print(f"DEBUG: GPUtil found {len(gpus)} GPUs.")
            sys.stdout.flush()

            if not gpus:
                print("DEBUG: No GPUs detected by GPUtil. Skipping GPU stats collection.")
                sys.stdout.flush()

            for gpu in gpus:
                gpu_dict = {
                    'gpu_id': gpu.id,
                    'ram_usage': round(gpu.memoryUsed, 2), # GPU memory used in MB
                    'ram_available': round(gpu.memoryFree, 2), # GPU memory free in MB
                    'temp': round(gpu.temperature, 2) # GPU temperature in Celsius
                }
                # Validate with GpuStatsCreateData (validation only)
                _ = GpuStatsCreateData(**gpu_dict)
                gpu_data_list.append(gpu_dict)
                print(f"DEBUG: GPU stats collected and validated for GPU ID {gpu.id}: {gpu_dict}")
                sys.stdout.flush()

        except Exception as gpu_e:
            print(f"WARNING: Could not retrieve GPU stats (GPUtil might not be installed or compatible, or no GPU detected): {gpu_e}")
            sys.stdout.flush()
            # gpu_data_list will remain empty if an error occurs, which is handled gracefully.

        # Return a single list with pc_data_dict as the first element, followed by each gpu_dict
        all_stats = [pc_data_dict] + gpu_data_list
        print(f"DEBUG: get_pc_stats returning: {all_stats}")
        sys.stdout.flush()
        return all_stats

    except Exception as e:
        print(f"ERROR: An error occurred while gathering PC stats: {e}")
        sys.stdout.flush()
        # import traceback
        # traceback.print_exc() # Uncomment for full traceback if needed
        return None # Return None if a critical error prevents data collection

async def insert_stats_to_db(stats_list: List[Dict[str, Union[float, int, None]]]) -> None:
    """
    Inserts PC and GPU statistics from a list into the database.
    This function will now raise any exceptions encountered during database insertion.

    Args:
        stats_list (List[Dict[str, Union[float, int, None]]]):
            A list where:
            - The first element is a dictionary containing PC statistics.
            - Subsequent elements are dictionaries for each detected GPU.
    """
    print(f"DEBUG: insert_stats_to_db called with {len(stats_list)} items.")
    sys.stdout.flush()

    if not stats_list:
        print("No stats to insert.")
        sys.stdout.flush()
        return

    pc_stats_inserted_count = 0
    gpu_stats_inserted_count = 0

    for item in stats_list:
        try:
            
            if 'gpu_id' in item:
                print(f"DEBUG: Attempting to insert GPU stats for GPU ID: {item.get('gpu_id')}...")
                sys.stdout.flush()
                await gpu_interface.create(item)
                gpu_stats_inserted_count += 1
                print(f"DEBUG: Successfully inserted GPU stats for GPU ID: {item.get('gpu_id')}.")
                sys.stdout.flush()
            else:
                
                if pc_stats_inserted_count == 0:
                    print("DEBUG: Attempting to insert PC stats...")
                    sys.stdout.flush()
                    await pc_interface.create(item)
                    pc_stats_inserted_count += 1
                    print("DEBUG: Successfully inserted PC stats.")
                    sys.stdout.flush()
                else:
                    print(f"WARNING: Skipping additional PC stats entry: {item}")
                    sys.stdout.flush()
        except Exception as insert_e:
            print(f"ERROR: Failed to insert stats for item {item}: {insert_e}")
            sys.stdout.flush()
            # import traceback
            # traceback.print_exc() # Uncomment for full traceback if needed

    if pc_stats_inserted_count > 0:
        print(f"{pc_stats_inserted_count} PC stats entry inserted successfully.")
        sys.stdout.flush()
    if gpu_stats_inserted_count > 0:
        print(f"{gpu_stats_inserted_count} GPU stats entries inserted successfully.")
        sys.stdout.flush()
    if pc_stats_inserted_count == 0 and gpu_stats_inserted_count == 0:
        print("No valid stats found to insert.")
        sys.stdout.flush()
